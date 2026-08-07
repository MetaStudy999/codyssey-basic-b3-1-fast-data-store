# Testing Guide

## Commands

```bash
python -m compileall -q src main.py tests
python -m unittest discover -s tests -v
python scripts/check_forbidden_builtins.py
```

## What is tested

- DLL head/tail/prev/next invariants and O(1) node move behavior
- Hash collision chaining
- load factor > 0.75 resize to 2x capacity
- heap ordering and empty boundaries
- all six String commands
- maxmemory LRU eviction and UTF-8 byte accounting
- TTL countdown, expiry, missing/no-TTL return values
- expired GET does not refresh LRU
- overwrite clears active TTL
- DEL clears data/LRU/active TTL state
- OOM rejects an oversized single entry without destroying an existing value
- quoted values and case-insensitive command names
- unknown command / wrong args / integer parsing error
- source scan for forbidden built-in Key-Value substitutions

## Evidence rule

`evidence/test-results.txt` and `evidence/repl-transcript.txt` contain actual command output captured from an executed local Python runtime. Expected examples are not labeled as evidence.
