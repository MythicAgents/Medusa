#!/usr/bin/env bash
# Run the agent_code syntax smoke tests under both Python 3 (locally) and
# Python 2.7 (via the official python:2.7 Docker image, since Python 2 is no
# longer packaged for modern distros).
#
# Usage:
#   tests/run_agent_code_syntax.sh           # run both py3 and py2 legs
#   tests/run_agent_code_syntax.sh py3       # run only the py3 leg
#   tests/run_agent_code_syntax.sh py2       # run only the py2 leg
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_PATH="tests/test_agent_code_syntax.py"
PY2_IMAGE="python:2.7-slim"
leg="${1:-all}"

run_py3() {
    echo "== Python 3 syntax check (local) =="
    python3 "$REPO_ROOT/$TEST_PATH" -v
}

run_py2() {
    echo "== Python 2.7 syntax check (docker: $PY2_IMAGE) =="
    if ! command -v docker >/dev/null 2>&1; then
        echo "docker not found; cannot run the Python 2.7 leg" >&2
        return 1
    fi
    docker run --rm -v "$REPO_ROOT":/src -w /src "$PY2_IMAGE" python "$TEST_PATH" -v
}

case "$leg" in
    py3) run_py3 ;;
    py2) run_py2 ;;
    all) run_py3; echo; run_py2 ;;
    *) echo "Usage: $0 [py3|py2|all]" >&2; exit 2 ;;
esac
