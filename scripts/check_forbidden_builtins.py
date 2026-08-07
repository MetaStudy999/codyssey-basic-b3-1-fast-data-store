"""Fail if implementation substitutes core storage with forbidden built-ins."""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
violations = []

for directory, _, filenames in os.walk(SRC):
    for filename in filenames:
        if not filename.endswith(".py"):
            continue
        path = os.path.join(directory, filename)
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
        tree = ast.parse(source, filename=path)

        for node in ast.walk(tree):
            if isinstance(node, (ast.Dict, ast.DictComp)):
                violations.append((path, node.lineno, "dict literal/comprehension"))
            if isinstance(node, (ast.Set, ast.SetComp)):
                violations.append((path, node.lineno, "set literal/comprehension"))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("dict", "set"):
                    violations.append((path, node.lineno, "built-in call " + node.func.id))
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "collections":
                        violations.append((path, node.lineno, "import collections"))
            if isinstance(node, ast.ImportFrom) and node.module == "collections":
                violations.append((path, node.lineno, "from collections import ..."))
            if isinstance(node, ast.Name) and node.id in ("Dict", "Set"):
                violations.append((path, node.lineno, "typing " + node.id))

if violations:
    for path, line_number, detail in violations:
        print("FORBIDDEN", os.path.relpath(path, ROOT), line_number, detail)
    sys.exit(1)

print("PASS: no forbidden dict/set/collections replacement detected in src/")
