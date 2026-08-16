#!/usr/bin/env bash
# B3-1 R01 verification-only helper.
# Reference mode: ./verify.sh
# Runtime mode:   ./verify.sh --runtime

set -u

PASS=0
FAIL=0
MODE="${1:-reference}"
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROUND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
REFERENCE="$ROUND_DIR/reference"
REPO_ROOT=$(cd "$SCRIPT_DIR/../../.." && pwd)
TEST_OUT=$(mktemp)
trap 'rm -f "$TEST_OUT"' EXIT
export PYTHONDONTWRITEBYTECODE=1

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

check_file() {
    if [ -f "$1" ]; then
        pass "file exists: ${1#$REPO_ROOT/}"
    else
        fail "file missing: ${1#$REPO_ROOT/}"
    fi
}

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[FAIL] Python not found"
    echo "Result: 0 PASS / 1 FAIL"
    exit 1
fi

VERSION=$($PYTHON -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
if $PYTHON -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,8) else 1)'; then
    pass "Python >= 3.8 ($VERSION)"
else
    fail "Python >= 3.8 required ($VERSION)"
fi

for file in \
  "$REFERENCE/main.py" \
  "$REFERENCE/mini_redis/__init__.py" \
  "$REFERENCE/mini_redis/doubly_linked_list.py" \
  "$REFERENCE/mini_redis/hash_map.py" \
  "$REFERENCE/mini_redis/min_heap.py" \
  "$REFERENCE/mini_redis/store.py" \
  "$REFERENCE/mini_redis/cli.py" \
  "$REFERENCE/tests/test_mini_redis.py" \
  "$REFERENCE/README.md" \
  "$ROUND_DIR/REFERENCE-BUILD.md" \
  "$ROUND_DIR/REFERENCE-STATUS.md" \
  "$ROUND_DIR/BEGINNER-GUIDE.md" \
  "$ROUND_DIR/CHECKLIST.md" \
  "$ROUND_DIR/docs/requirements-mapping.md" \
  "$ROUND_DIR/docs/evaluation-qa.md" \
  "$ROUND_DIR/evidence/README.md"; do
    check_file "$file"
done

if REFERENCE="$REFERENCE" $PYTHON <<'PY'
import ast
import os
import sys

root = os.environ["REFERENCE"]
failures = []
for current_root, _, files in os.walk(root):
    for name in files:
        if not name.endswith(".py"):
            continue
        path = os.path.join(current_root, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                ast.parse(handle.read(), filename=path)
        except SyntaxError as exc:
            failures.append("{}:{} {}".format(path, exc.lineno, exc.msg))
if failures:
    for item in failures:
        print(item)
    sys.exit(1)
PY
then
    pass "Python AST syntax parse"
else
    fail "Python syntax parse"
fi

if PYTHONPATH="$REFERENCE" $PYTHON -m unittest discover -s "$REFERENCE/tests" -p 'test_*.py' >"$TEST_OUT" 2>&1; then
    pass "Reference unit tests"
else
    fail "Reference unit tests"
    echo "----- unittest output -----"
    cat "$TEST_OUT"
    echo "---------------------------"
fi

if REFERENCE="$REFERENCE" $PYTHON <<'PY'
import ast
import os
import sys

root = os.path.join(os.environ["REFERENCE"], "mini_redis")
violations = []
for name in os.listdir(root):
    if not name.endswith(".py"):
        continue
    path = os.path.join(root, name)
    with open(path, "r", encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=path)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Dict, ast.Set, ast.DictComp, ast.SetComp)):
            violations.append((name, node.lineno, type(node).__name__))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("dict", "set"):
            violations.append((name, node.lineno, "call " + node.func.id))
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "collections" or alias.name.startswith("collections."):
                    violations.append((name, node.lineno, "import collections"))
                if alias.name == "heapq" or alias.name.startswith("heapq."):
                    violations.append((name, node.lineno, "import heapq"))
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == "collections" or node.module.startswith("collections."):
                violations.append((name, node.lineno, "from collections"))
            if node.module == "heapq" or node.module.startswith("heapq."):
                violations.append((name, node.lineno, "from heapq"))
if violations:
    for item in violations:
        print("forbidden:", item)
    sys.exit(1)
PY
then
    pass "no dict/set/collections/heapq in core implementation"
else
    fail "forbidden collection/heap usage detected"
fi

if PYTHONPATH="$REFERENCE" $PYTHON - <<'PY'
from mini_redis.cli import ERR_OOM, execute
from mini_redis.store import MiniRedis

s = MiniRedis()
checks = [
    execute(s, "SET name Alice") == "OK",
    execute(s, "GET name") == '"Alice"',
    execute(s, "EXISTS name") == "(integer) 1",
    execute(s, "DBSIZE") == "(integer) 1",
    '"name"' in execute(s, "KEYS"),
    execute(s, "DEL name") == "(integer) 1",
    execute(s, "GET name") == "(nil)",
]

m = MiniRedis()
checks.extend([
    execute(m, "CONFIG SET maxmemory 3") == "OK",
    execute(m, "SET a 1") == "OK",
    execute(m, "SET long value") == ERR_OOM,
    execute(m, "GET a") == '"1"',
    "used_memory:" in execute(m, "INFO memory"),
    "maxmemory:3" in execute(m, "INFO memory"),
    "evicted_keys:" in execute(m, "INFO memory"),
])

raise SystemExit(0 if all(checks) else 1)
PY
then
    pass "basic/OOM command smoke test"
else
    fail "basic/OOM command smoke test"
fi

if command -v git >/dev/null 2>&1 && git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    TRACKED=$(git -C "$REPO_ROOT" ls-files 'training/round-01-clear/**' | grep -E '(^|/)(\.env($|\.)|.*\.(key|pem)$|secrets/)' || true)
    [ -z "$TRACKED" ] && pass "no tracked Secret-pattern files" || fail "tracked Secret-pattern files detected"
fi

if [ "$MODE" = "--runtime" ] || [ "$MODE" = "runtime" ]; then
    RUNTIME_DIR="$ROUND_DIR/evidence/runtime"
    VERIFY_OUT="$RUNTIME_DIR/verify-output.txt"
    REPL_OUT="$RUNTIME_DIR/repl-session.txt"
    SELF_CHECK="$RUNTIME_DIR/evaluation-self-check.md"

    check_file "$VERIFY_OUT"
    check_file "$REPL_OUT"
    check_file "$SELF_CHECK"

    if [ -f "$VERIFY_OUT" ] && grep -Eq 'Result: [0-9]+ PASS / 0 FAIL' "$VERIFY_OUT"; then
        pass "runtime verify output records 0 FAIL"
    else
        fail "runtime verify output must record Result: N PASS / 0 FAIL"
    fi

    if [ -f "$REPL_OUT" ]; then
        missing=0
        for token in 'SET ' 'GET ' 'DEL ' 'EXISTS ' 'DBSIZE' 'KEYS' 'CONFIG SET maxmemory' 'INFO memory' 'EXPIRE ' 'TTL ' 'OOM' '(error)'; do
            if ! grep -Fq "$token" "$REPL_OUT"; then
                echo "[MISSING RUNTIME TOKEN] $token"
                missing=1
            fi
        done
        [ "$missing" -eq 0 ] && pass "runtime REPL covers required command/error groups" || fail "runtime REPL coverage incomplete"
    fi

    if [ -d "$RUNTIME_DIR" ] && grep -RIEq '(password|api[_-]?key|access[_-]?token|private[_-]?key)[[:space:]]*[:=][[:space:]]*[^[:space:]]+' "$RUNTIME_DIR" 2>/dev/null; then
        fail "possible Secret/credential text found in runtime Evidence"
    else
        pass "no obvious Secret/credential assignment in runtime Evidence"
    fi
fi

echo
printf 'Result: %d PASS / %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
