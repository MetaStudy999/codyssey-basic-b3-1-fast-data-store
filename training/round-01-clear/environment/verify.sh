#!/usr/bin/env bash
# B3-1 R01 verification-only helper.

set -u

PASS=0
FAIL=0
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROUND_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
REFERENCE="$ROUND_DIR/reference"

pass() { echo "[PASS] $1"; PASS=$((PASS + 1)); }
fail() { echo "[FAIL] $1"; FAIL=$((FAIL + 1)); }

if command -v python3 >/dev/null 2>&1; then
    PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON=python
else
    echo "[FAIL] Python not found"
    echo "Result: 0 PASS / 1 FAIL"
    exit 1
fi

if $PYTHON -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,8) else 1)'; then
    pass "Python >= 3.8"
else
    fail "Python >= 3.8 required"
fi

for file in \
  "$REFERENCE/main.py" \
  "$REFERENCE/mini_redis/doubly_linked_list.py" \
  "$REFERENCE/mini_redis/hash_map.py" \
  "$REFERENCE/mini_redis/min_heap.py" \
  "$REFERENCE/mini_redis/store.py" \
  "$REFERENCE/mini_redis/cli.py" \
  "$REFERENCE/tests/test_mini_redis.py"; do
    [ -f "$file" ] && pass "file exists: ${file#$ROUND_DIR/}" || fail "file missing: ${file#$ROUND_DIR/}"
done

if PYTHONPATH="$REFERENCE" $PYTHON -m compileall -q "$REFERENCE"; then
    pass "Python syntax compile"
else
    fail "Python syntax compile"
fi

if PYTHONPATH="$REFERENCE" $PYTHON -m unittest discover -s "$REFERENCE/tests" -p 'test_*.py' >/tmp/b3-1-tests.out 2>&1; then
    pass "Reference unit tests"
else
    fail "Reference unit tests (see /tmp/b3-1-tests.out)"
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
        if isinstance(node, ast.ImportFrom) and node.module and (node.module == "collections" or node.module.startswith("collections.")):
            violations.append((name, node.lineno, "from collections"))
if violations:
    for item in violations:
        print("forbidden:", item)
    sys.exit(1)
PY
then
    pass "no dict/set/collections in core implementation"
else
    fail "forbidden built-in key-value collection usage detected"
fi

if PYTHONPATH="$REFERENCE" $PYTHON - <<'PY'
from mini_redis.cli import execute
from mini_redis.store import MiniRedis
s = MiniRedis()
checks = [
    execute(s, "SET name Alice") == "OK",
    execute(s, "GET name") == '"Alice"',
    execute(s, "EXISTS name") == "(integer) 1",
    execute(s, "DBSIZE") == "(integer) 1",
    execute(s, "DEL name") == "(integer) 1",
]
raise SystemExit(0 if all(checks) else 1)
PY
then
    pass "basic command smoke test"
else
    fail "basic command smoke test"
fi

echo
printf 'Result: %d PASS / %d FAIL\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
