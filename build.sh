#!/usr/bin/env bash
# Build and test this copy of BeautifulSoup (with the Milestone-2 additions).
#
# Usage:   ./build.sh [--no-tests] [--no-package]
#   (default)     create .venv, install dependencies, install the library in
#                 editable mode, run the test-suite, build sdist + wheel in dist/
#   --no-tests    skip running pytest
#   --no-package  skip building the sdist/wheel
#
# Needs: Python >= 3.10 on PATH (override with PYTHON=python3.11 ./build.sh)
#        and network access to PyPI the first time (to install dependencies).
set -euo pipefail

cd "$(dirname "$0")"          # always run from the repository root

RUN_TESTS=1
BUILD_PACKAGE=1
for arg in "$@"; do
  case "$arg" in
    --no-tests)   RUN_TESTS=0 ;;
    --no-package) BUILD_PACKAGE=0 ;;
    -h|--help)    sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

PYTHON="${PYTHON:-python3}"
if ! "$PYTHON" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
  echo "error: Python >= 3.10 is required (tried '$PYTHON'). Set PYTHON=/path/to/python3.10+" >&2
  exit 1
fi

echo "==> Creating virtual environment in .venv"
if [ ! -d .venv ]; then
  "$PYTHON" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing dependencies"
python -m pip install --quiet --upgrade pip
# lxml and html5lib are optional parsers that the test-suite also exercises.
python -m pip install --quiet pytest build lxml html5lib

echo "==> Installing the library (editable)"
python -m pip install --quiet -e .

if [ "$RUN_TESTS" -eq 1 ]; then
  echo "==> Running tests"
  python -m pytest bs4/tests -q
fi

if [ "$BUILD_PACKAGE" -eq 1 ]; then
  echo "==> Building sdist and wheel into dist/"
  rm -rf dist
  python -m build
  ls -1 dist
fi

echo "==> Done. Activate the environment with: source .venv/bin/activate"
