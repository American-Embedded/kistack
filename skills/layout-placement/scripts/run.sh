#!/bin/sh
# Run one of this skill's scripts in its own Python environment:
#   scripts/run.sh move.py board.kicad_pcb C4=146.2,101.89,90 --save
# The environment is made once from requirements.txt (exact versions, with
# hashes) under ${XDG_CACHE_HOME:-~/.cache}/kistack/layout-placement/<hash>,
# with uv when it is installed, else with python3 (3.12 or newer) and pip.
# Nothing is installed anywhere else. LAYOUT_PLACEMENT_PYTHON names a Python
# that already has the requirements, and skips the environment.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
case ${1:-} in
  ipc_board.py|pin_sides.py|route_check.py|move.py|group_search.py|placement_audit.py|local_search.py|grid_router.py) ;;
  *) echo "usage: run.sh SCRIPT.py ARGS... (SCRIPT one of: pin_sides route_check move group_search placement_audit local_search)" >&2; exit 2;;
esac
script=$1; shift
export PYTHONDONTWRITEBYTECODE=1
if [ -n "${LAYOUT_PLACEMENT_PYTHON:-}" ]; then
  exec "$LAYOUT_PLACEMENT_PYTHON" -s "$here/$script" "$@"
fi
req=$here/../requirements.txt
sha() { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -c1-16; }
env=${XDG_CACHE_HOME:-$HOME/.cache}/kistack/layout-placement/$(sha "$req")
# an environment whose interpreter has gone (a Python uninstalled) is made again
if [ -f "$env/.ready" ] && ! "$env/bin/python" -s -c '' 2>/dev/null; then
  rm -rf "$env"
fi
if [ ! -f "$env/.ready" ]; then
  mkdir -p "$(dirname "$env")"
  tmp=$(mktemp -d "$env.new.XXXXXX")
  trap 'rm -rf "$tmp"' EXIT
  if command -v uv >/dev/null 2>&1; then
    uv venv --quiet --python '>=3.12' "$tmp" >&2
    uv pip install --quiet --python "$tmp/bin/python" --require-hashes -r "$req" >&2
  else
    py=$(command -v python3) || { echo "run.sh: needs uv, or python3 3.12 or newer" >&2; exit 1; }
    "$py" -c 'import sys; sys.exit(sys.version_info < (3, 12))' || { echo "run.sh: $py is older than 3.12; install uv or a newer python3" >&2; exit 1; }
    "$py" -m venv "$tmp" >&2
    "$tmp/bin/python" -m pip install --quiet --disable-pip-version-check --require-hashes -r "$req" >&2
  fi
  "$tmp/bin/python" -s -c 'import kipy, shapely, numpy' >&2
  : > "$tmp/.ready"
  # only bin/python is used, and it finds its environment after the rename.
  # rename(2) fails on a folder that is there and not empty, so a run that
  # got there first wins and this one's copy is removed
  [ -d "$env" ] && [ ! -f "$env/.ready" ] && rm -rf "$env"
  "$tmp/bin/python" -s -c 'import os, sys
try:
    os.rename(sys.argv[1], sys.argv[2])
except OSError:
    pass' "$tmp" "$env"
  rm -rf "$tmp"
  trap - EXIT
  [ -f "$env/.ready" ] || { echo "run.sh: could not set up $env" >&2; exit 1; }
fi
exec "$env/bin/python" -s "$here/$script" "$@"
