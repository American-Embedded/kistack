#!/usr/bin/env python3
"""Headless checks of skills/layout-placement on synthetic boards.

    KICAD_CLI=/path/to/kicad-cli python3 tests/layout-placement/test_layout_placement.py [--v18 DIR]

Starts its own `kicad-cli api-server` processes on boards made by
make_fixture.py in a temporary folder (never a real project, never a
Backplane server: every script gets KICAD_API_SOCKET or
LAYOUT_PLACEMENT_SOCKETS pointing at this test's own sockets). The skill's
scripts run through scripts/run.sh, so the first run also sets up their
Python environment from requirements.txt.

--skill DIR: test another copy of the skill (a packaged one) instead.
--v18 DIR: the frozen v18 skill folder; its route_check.py and
placement_audit.py must print the same as this copy's on a board whose rules
are v18's built-in ones.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, "..", "..", "skills", "layout-placement"))
FAILS = []
PASSES = []


def check(name, ok, detail=""):
    (PASSES if ok else FAILS).append(name)
    print(("ok   " if ok else "FAIL ") + name + ("" if ok or not detail else "\n     " + detail.replace("\n", "\n     ")))


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def fixture(d, name="fixture", *extra):
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_fixture.py"), d, "--name", name, *extra], check=True)
    return os.path.join(d, name + ".kicad_pcb")


class Server:
    def __init__(self, cli, board, sockdir):
        os.makedirs(sockdir, exist_ok=True)
        self.sock = os.path.join(sockdir, "api.sock")
        env = dict(os.environ)
        env.pop("DISPLAY", None)
        env.pop("WAYLAND_DISPLAY", None)
        self.log = open(os.path.join(sockdir, "server.log"), "w")
        self.p = subprocess.Popen([cli, "api-server", "--socket", self.sock, "--parent-pid", str(os.getpid()),
                                   "--idle-exit", "600", board], stdout=self.log, stderr=subprocess.STDOUT, env=env,
                                  start_new_session=True)
        for _ in range(120):
            if os.path.exists(self.sock):
                break
            if self.p.poll() is not None:
                raise SystemExit(f"api-server exited {self.p.returncode}; see {self.log.name}")
            time.sleep(0.25)
        else:
            raise SystemExit("api-server did not open its socket")
        time.sleep(0.5)

    @property
    def url(self):
        return "ipc://" + self.sock

    def stop(self):
        if self.p.poll() is None:
            self.p.send_signal(signal.SIGTERM)
            try:
                self.p.wait(10)
            except subprocess.TimeoutExpired:
                self.p.kill()
        self.log.close()


def run(script, *args, env=None, extra_env=None):
    e = dict(os.environ)
    e.pop("KICAD_API_SOCKET", None)
    e.update(env or {})
    e.update(extra_env or {})
    return subprocess.run([os.path.join(SKILL, "scripts", "run.sh"), script, *args], capture_output=True, text=True, env=e, timeout=600)


def pose_of(board, ref, sock):
    """A footprint's (x, y, rot, side) as the server sees it, through the skill's own loader."""
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import ipc_board as g; "
            "f = g.by_ref(g.load(sys.argv[2]))[sys.argv[3]]; print(f'{f.x:.4f} {f.y:.4f} {f.rot:.1f} {f.layer}')")
    py = venv_python()
    r = subprocess.run([py, "-s", "-c", code, os.path.join(SKILL, "scripts"), board, ref], capture_output=True,
                       text=True, env={**os.environ, "KICAD_API_SOCKET": sock, "PYTHONDONTWRITEBYTECODE": "1"})
    if r.returncode:
        raise SystemExit(r.stderr)
    return r.stdout.split()


def venv_python():
    with open(os.path.join(SKILL, "requirements.txt"), "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()[:16]
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, "kistack", "layout-placement", h, "bin", "python")


FAULT = r'''
import runpy, sys
sys.path.insert(0, sys.argv[1])
from kipy.board import Board
real_push, real_fps = Board.push_commit, Board.get_footprints
state = {"pushes": 0}
def push(self, c, m=""):
    state["pushes"] += 1
    return real_push(self, c, m)
def fps(self):
    out = list(real_fps(self))
    # after the first commit only: pretend a footprint vanished
    return out[:-1] if state["pushes"] == 1 else out
Board.push_commit, Board.get_footprints = push, fps
sys.argv = [sys.argv[2]] + sys.argv[3:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v18", help="the frozen v18 layout-placement folder, to compare outputs")
    ap.add_argument("--keep", action="store_true", help="keep the temporary folder")
    ap.add_argument("--skill", help="the layout-placement folder to test (default: this repository's), "
                                    "e.g. a packaged copy")
    a = ap.parse_args()
    global SKILL
    if a.skill:
        SKILL = os.path.realpath(a.skill)
    print("testing", SKILL)
    cli = os.environ.get("KICAD_CLI") or shutil.which("kicad-cli")
    if not cli:
        sys.exit("set KICAD_CLI to a kicad-cli with api-server")
    tmp = tempfile.mkdtemp(prefix="layout-placement-test.")
    servers = []
    try:
        proj = os.path.join(tmp, "proj")
        board = fixture(os.path.join(proj, "board"))
        with open(os.path.join(proj, ".backplane.json"), "w") as f:
            json.dump({"pcb": "board/fixture.kicad_pcb", "other": "kept"}, f)
        other = fixture(os.path.join(proj, "alt"), "other")
        bare = fixture(os.path.join(tmp, "bare"), "bare", "--no-project")
        wide = fixture(os.path.join(tmp, "wide"), "wide", "--track", "0.2", "--clearance", "0.15", "--via", "0.6")
        companion = board + ".backplane.json"
        with open(board) as f:
            u1 = re.search(r'\(footprint "fixture:U1" \(layer "F.Cu"\) \(uuid "([0-9a-f-]+)"\)', f.read()).group(1)
        # KiCad removes a companion file with no items, so give U1 a property to keep
        meta = {"format": "backplane-kicad-metadata", "version": 1,
                "items": {u1: {"custom_properties": {"fixture.note": "kept"}}}}
        with open(companion, "w") as f:
            json.dump(meta, f)
        shutil.copy(companion, os.path.join(tmp, "companion.orig"))
        s1 = Server(cli, board, os.path.join(tmp, "s1"))
        servers.append(s1)
        s2 = Server(cli, other, os.path.join(tmp, "s2"))
        servers.append(s2)
        S1 = {"KICAD_API_SOCKET": s1.url}

        # reading, and the environment set up from scratch
        r = run("pin_sides.py", board, "U1", env=S1)
        check("pin_sides reads the board", r.returncode == 0 and "pin   1 VDD" in r.stdout, r.stderr + r.stdout)
        check("python environment is the private one", os.path.exists(venv_python()), venv_python())
        r = run("pin_sides.py", board, "U9", env=S1)
        check("unknown part refused", r.returncode != 0 and "no footprint U9" in r.stderr, r.stderr)

        # binding to the right board
        r = run("pin_sides.py", board, "U1", env={"KICAD_API_SOCKET": s2.url})
        check("socket with another board refused", r.returncode != 0 and "not " + os.path.realpath(board) in r.stderr,
              r.stderr)
        r = run("pin_sides.py", other, "U1", env={"KICAD_API_SOCKET": s2.url})
        check("board that is not the project's refused", r.returncode != 0 and "is not the project's board" in r.stderr,
              r.stderr)
        r = run("pin_sides.py", other, "U1", env={"KICAD_API_SOCKET": s2.url, "LAYOUT_PLACEMENT_ALTERNATE": "1"})
        check("alternate board allowed when asked", r.returncode == 0, r.stderr)
        globs = os.path.join(tmp, "s*", "api.sock")
        r = run("pin_sides.py", board, "U1", env={"LAYOUT_PLACEMENT_SOCKETS": globs})
        check("discovery finds the one server with the board", r.returncode == 0, r.stderr)
        s3 = Server(cli, board, os.path.join(tmp, "s3"))
        servers.append(s3)
        r = run("pin_sides.py", board, "U1", env={"LAYOUT_PLACEMENT_SOCKETS": globs})
        check("two servers with the board refused", r.returncode != 0 and "2 KiCad servers have" in r.stderr, r.stderr)
        s3.stop()
        servers.remove(s3)
        r = run("pin_sides.py", board, "U1", env={"LAYOUT_PLACEMENT_SOCKETS": os.path.join(tmp, "none", "*.sock")})
        check("no server refused", r.returncode != 0 and "no KiCad API server has" in r.stderr, r.stderr)

        # moves: refused before anything changes
        before_file = sha(board)
        before_c1 = pose_of(board, "C1", s1.url)
        for args, word in ((["C1=105,95,90", "C1=105,96,0"], "repeated: C1"), (["C1=105,95"], "bad move"),
                           (["C1=105,x,90"], "bad move"), (["C1=105,95,90,Q"], "bad move"),
                           (["C1=nan,95,90"], "bad move"), (["C9=105,95,90"], "no footprint C9")):
            r = run("move.py", board, *args, "--save", env=S1)
            check(f"move {' '.join(args)} refused", r.returncode != 0 and word in r.stderr, r.stderr)
        check("refused moves left the server alone", pose_of(board, "C1", s1.url) == before_c1)
        check("refused moves left the file alone", sha(board) == before_file)

        # a move without --save changes the server, not the file
        r = run("move.py", board, "C1=104.5,98.5,90", env=S1)
        check("move without --save", r.returncode == 0 and "not saved" in r.stdout, r.stderr + r.stdout)
        check("server has the move", pose_of(board, "C1", s1.url)[:3] == ["104.5000", "98.5000", "90.0"],
              str(pose_of(board, "C1", s1.url)))
        check("file unchanged without --save", sha(board) == before_file)

        # an integrity failure after the commit puts the parts back
        fault = os.path.join(tmp, "fault.py")
        with open(fault, "w") as f:
            f.write(FAULT)
        e = {**os.environ, **S1, "PYTHONDONTWRITEBYTECODE": "1"}
        r = subprocess.run([venv_python(), "-s", fault, os.path.join(SKILL, "scripts"),
                            os.path.join(SKILL, "scripts", "move.py"), board, "C1=103,97,0", "--save"],
                           capture_output=True, text=True, env=e)
        check("integrity failure reported", r.returncode != 0 and "footprint count changed" in r.stderr
              and "the parts were put back" in r.stderr, r.stderr)
        check("integrity failure restored the part", pose_of(board, "C1", s1.url)[:3] == ["104.5000", "98.5000", "90.0"],
              str(pose_of(board, "C1", s1.url)))
        check("integrity failure did not save", sha(board) == before_file)

        # a position KiCad cannot take is dropped, not half applied
        r = run("move.py", board, "C1=104.5,98.5,90", "C2=5000000,0,0", "--save", env=S1)
        check("out-of-range move refused", r.returncode != 0, r.stderr + r.stdout)
        print("     (" + (r.stderr.strip().splitlines() or ["no message"])[-1][:200] + ")")
        check("out-of-range move left the file alone", sha(board) == before_file)

        # --save writes the configured board, and nothing else
        cfg_before = sha(os.path.join(proj, ".backplane.json"))
        r = run("move.py", board, "C1=104.6,98.4,90", "C3=104.8,101.6,180", "--save", env=S1)
        check("move with --save", r.returncode == 0 and "saved " + os.path.realpath(board) in r.stdout,
              r.stderr + r.stdout)
        check("file changed by --save", sha(board) != before_file)
        with open(board) as f:
            text = f.read()
        check("saved file has the new position", re.search(r"\(at\s+104\.6\s+98\.4\s+90\)|\(translate\s+104\.6\s+98\.4\)\s*\(rotate\s+90\)", text) is not None,
              "C1 position not found in the file")
        # Backplane KiCad rewrites <board>.backplane.json on every save from what it
        # attached on load; move.py --save must leave it exactly as a plain
        # SaveDocument of the same board does
        ctrl_dir = os.path.join(tmp, "ctrl")
        shutil.copytree(os.path.join(proj, "board"), ctrl_dir)
        shutil.copy(os.path.join(tmp, "companion.orig"), os.path.join(ctrl_dir, "fixture.kicad_pcb.backplane.json"))
        sc = Server(cli, os.path.join(ctrl_dir, "fixture.kicad_pcb"), os.path.join(tmp, "sc"))
        servers.append(sc)
        code = ("import sys; from kipy import KiCad; KiCad(socket_path=sys.argv[1], timeout_ms=15000).get_board().save()")
        subprocess.run([venv_python(), "-s", "-c", code, sc.url], check=True, capture_output=True)
        sc.stop()
        servers.remove(sc)

        def companion_of(path):
            if not os.path.exists(path):
                return None
            with open(path) as f:
                return json.load(f)
        mine, plain = companion_of(companion), companion_of(os.path.join(ctrl_dir, "fixture.kicad_pcb.backplane.json"))
        check("companion metadata handled as KiCad's own save", mine == plain,
              f"move.py: {json.dumps(mine)[:200]}  plain save: {json.dumps(plain)[:200]}")
        print(f"     (after save the companion file is {'absent' if mine is None else 'present'})")
        check(".backplane.json kept", sha(os.path.join(proj, ".backplane.json")) == cfg_before)
        drc = os.path.join(tmp, "drc.json")
        subprocess.run([cli, "pcb", "drc", "--format", "json", "-o", drc, board], capture_output=True)
        with open(drc) as f:
            kinds = {v["type"] for v in json.load(f)["violations"]}
        check("saved board loads in kicad-cli DRC, no courtyard overlap", "courtyards_overlap" not in kinds, str(kinds))

        # rules come from the board, or from flags, never from defaults
        r = run("route_check.py", board, "--ic", "U1", env=S1)
        check("route_check runs", r.returncode == 0 and "all local links together" in r.stdout, r.stderr + r.stdout)
        check("route_check names the board's rules",
              "track width 0.150 mm (fixture.kicad_pro)" in r.stderr and "via diameter 0.500 mm" in r.stderr, r.stderr)
        r = run("placement_audit.py", board, "--ic", "U1", env=S1)
        check("placement_audit runs", r.returncode == 0 and "fronts (" in r.stdout, r.stderr)
        r = run("local_search.py", board, "--ic", "U1", "--pin", "1", "--part", "C1", "--top", "2", env=S1)
        check("local_search runs", r.returncode == 0 and "legal candidates" in r.stdout, r.stderr)
        r = run("group_search.py", board, "--ic", "U1", "--assign", "C1:1", "C2:11", "--top", "1", env=S1)
        check("group_search runs", r.returncode == 0 and "order " in r.stdout, r.stderr)

        sb = Server(cli, bare, os.path.join(tmp, "sb"))
        servers.append(sb)
        SB = {"KICAD_API_SOCKET": sb.url}
        r = run("route_check.py", bare, "--ic", "U1", env=SB)
        check("board without rules refused", r.returncode != 0 and "pass --track --clear --via --edge" in r.stderr,
              r.stderr)
        r = run("route_check.py", bare, "--ic", "U1", "--track", "0.15", "--clear", "0.1", "--via", "0.5", "--edge",
                "0.2", env=SB)
        check("board without rules runs with flags", r.returncode == 0 and "(flag)" in r.stderr, r.stderr)
        r = run("local_search.py", bare, "--ic", "U1", "--pin", "1", "--part", "C1", "--track", "0.15",
                "--clear", "0.1", env=SB)
        check("local_search needs only track and clearance", r.returncode == 0, r.stderr)
        sb.stop()
        servers.remove(sb)

        sw = Server(cli, wide, os.path.join(tmp, "sw"))
        servers.append(sw)
        r = run("route_check.py", wide, "--ic", "U1", env={"KICAD_API_SOCKET": sw.url})
        check("other rules are read", r.returncode == 0 and "track width 0.200 mm" in r.stderr
              and "clearance 0.150 mm" in r.stderr and "via diameter 0.600 mm" in r.stderr, r.stderr)

        if a.v18:
            for script, args in (("route_check.py", ["--ic", "U1"]), ("placement_audit.py", ["--ic", "U1"])):
                old = subprocess.run([venv_python(), "-s", os.path.join(a.v18, "scripts", script), board, *args],
                                     capture_output=True, text=True, env={**os.environ, **S1,
                                                                          "PYTHONDONTWRITEBYTECODE": "1"})
                new = run(script, board, *args, env=S1)
                check(f"{script} prints what v18 printed on v18's rules", old.returncode == 0 and
                      old.stdout == new.stdout, f"v18 rc {old.returncode}: {old.stderr[-400:]}")
    finally:
        for s in servers:
            s.stop()
        if a.keep:
            print("kept", tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f"{len(PASSES)} passed, {len(FAILS)} failed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
