# B3-1 Mission Work Packet — Mini Redis

> Finalized: 2026-08-08  
> Control Tower `MetaStudy999/codyssey-basic` was READ ONLY; only the B3-1 Mission Repository was modified.

## 1. Identity

- Mission ID: `B3-1`
- Mission Title: 정보를 엄청 빠르게 찾아주는 작은 저장소 만들기
- Mission Repository: `MetaStudy999/codyssey-basic-b3-1-fast-data-store`
- Workcell: `Chat 5 / B3-1`
- Started At: `2026-08-08T04:36:00+09:00`
- Mission PR: `https://github.com/MetaStudy999/codyssey-basic-b3-1-fast-data-store/pull/1`
- Mission Final Commit: `f5222c358b8705eccb2895ae95a0de414fdda3a6`
- Merge Status: `MERGED / squash`

## 2. Control Tower Baseline

- Repository: `MetaStudy999/codyssey-basic`
- Frozen Baseline SHA: `0d1581b3e82366988f57e1d76da311c028b8e15e`
- Current Control Tower main observed at G1: `f6192ad701bd1d2c317f908d210e7049f6b32310`
- Drift: `FOUND / NON-BLOCKING`
- Action: `CONTINUE_WITH_FROZEN_BASELINE`

The post-baseline Control Tower changes were limited to wave/launcher/governance presentation updates and did not alter the B3-1 Mission contract.

## 3. Read / Write Boundary

### READ

- Control Tower frozen baseline
- B3-1 Mission Repository
- B3-1 Mission/Evaluation Source

### WRITE

- `MetaStudy999/codyssey-basic-b3-1-fast-data-store`
- implementation branch: `mission/b3-1`
- final Handoff/result metadata: Mission Repository `main` after PR merge

### DO NOT WRITE

- `MetaStudy999/codyssey-basic`
- any other Mission Repository

## 4. Source Inventory

| Source | Type | State | Location | Result |
|---|---|---|---|---|
| Mission | PDF | `VALID` | `b3-1-mission.pdf` | authoritative 8-page Mission |
| Mission | Markdown | `DUPLICATE` | `b3-1-mission.md` | PDF transcription |
| Evaluation | Markdown | `VALID` | `b3-1-evaluation.md` | substantive official evaluation checklist |
| Governance | Markdown | `VALID` | frozen Control Tower baseline | execution rules only |

- Source Mode: `FULL SOURCE`
- Source Confidence: `HIGH`
- Blocking Source Gap: `NONE`

## 5. Mission Contract

### Goal

내장 Key-Value 컬렉션으로 핵심 저장 구조를 대체하지 않고 Hash Map, Doubly Linked List, Min Heap을 직접 구현하여 CLI 기반 Mini Redis의 LRU, TTL, memory limit 동작을 재현한다.

### Required Deliverables

- [x] Python CLI Mini Redis
- [x] custom Hash Map / Doubly Linked List / Min Heap
- [x] automated tests
- [x] README / requirement mapping / testing guide
- [x] actual test and REPL Evidence
- [x] learning material matching the implementation
- [x] `HANDOFF.md`
- [x] `mission-result.yaml`

### Required Behaviors

- [x] `SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS`
- [x] `CONFIG SET maxmemory`, `INFO memory`
- [x] `EXPIRE`, `TTL`
- [x] `mini-redis>` REPL and `exit`/`quit`
- [x] Redis-style OK/nil/integer/error output
- [x] custom hash function + chaining + resize when load factor > 0.75
- [x] DLL node with `prev`, `next`, `data`; known-node insertion/removal/move O(1)
- [x] Min Heap `push/pop/peek/size`, `_heapify_up`, `_heapify_down`
- [x] SET and successful GET update LRU
- [x] expired GET deletes first and does not refresh LRU
- [x] overwrite SET clears active TTL
- [x] DEL removes data/LRU/active TTL state
- [x] official UTF-8 key/value byte memory formula
- [x] LRU eviction until within maxmemory; `evicted_keys` increments
- [x] single entry larger than maxmemory rejected with OOM without storage
- [x] TTL return rules `-2`, `-1`, `N`
- [x] unknown/wrong-args/integer/OOM errors
- [x] quoted value support

### Constraints Confirmed

- Python 3.8+; verified using Python 3.13.5
- no `dict`, `set`, or `collections` substitution for core storage
- core structures split into separate modules
- docstrings/comments provided

### Explicit Non-scope

- networking
- persistence
- Redis List/Set/Sorted Set
- concurrency/locks
- optional bonus data structures and Pub/Sub

## 6. Requirement Traceability

| ID | Requirement | Implementation | Validation | Status |
|---|---|---|---|---|
| REQ-B3-1-001 | six String commands | `store.py`, `cli.py` | unit + REPL | PASS |
| REQ-B3-1-002 | maxmemory / INFO | `store.py` | memory/LRU tests + REPL | PASS |
| REQ-B3-1-003 | EXPIRE / TTL | active TTL map + heap | fake clock + real REPL | PASS |
| REQ-B3-1-004 | REPL / errors | `cli.py` | parser tests + transcript | PASS |
| REQ-B3-1-005 | custom DLL / O(1) | `doubly_linked_list.py` | invariants + explanation | PASS |
| REQ-B3-1-006 | custom Hash Map | `hash_map.py` | collision + resize tests | PASS |
| REQ-B3-1-007 | custom Min Heap | `min_heap.py` | ordering/boundary tests | PASS |
| REQ-B3-1-008 | LRU eviction | Entry -> DLL node | deterministic tests | PASS |
| REQ-B3-1-009 | TTL/LRU edge cases | lazy heap + active TTL map | overwrite/delete/expired/purge tests | PASS |
| REQ-B3-1-010 | prohibited built-in KV replacement | custom structures | AST scan | PASS |
| REQ-B3-1-011 | module separation / docs | `src/mini_redis/*` | repository review | PASS |
| REQ-B3-1-012 | explainable structure/complexity/extensions | `docs/learning.md` | evaluation mapping | PASS |

## 7. Evaluation Mapping

| Evaluation | Validation | Evidence | Status |
|---|---|---|---|
| base commands | unit + CLI | test results / transcript | PASS |
| LRU maxmemory eviction | unit + CLI | test results / transcript | PASS |
| INFO memory | unit + CLI | transcript | PASS |
| EXPIRE / TTL | fake-clock + real wait | test results / transcript | PASS |
| error standard | CLI tests | test results / transcript | PASS |
| DLL O(1) explanation | code-linked learning | `docs/learning.md` | PASS |
| hash/chaining/resize explanation | code-linked learning | `docs/learning.md` | PASS |
| LRU/TTL/memory/GET flow | code-linked learning | `docs/learning.md` | PASS |
| LFU / 100k / overhead / fair scoring | extension section | `docs/learning.md` | PASS |

## 8. Repository Result Structure

```text
.
├── AGENTS.md
├── MISSION-WORK-PACKET.md
├── HANDOFF.md
├── mission-result.yaml
├── README.md
├── main.py
├── b3-1-mission.pdf
├── b3-1-mission.md
├── b3-1-evaluation.md
├── src/mini_redis/
│   ├── __init__.py
│   ├── cli.py
│   ├── doubly_linked_list.py
│   ├── hash_map.py
│   ├── min_heap.py
│   └── store.py
├── tests/
│   ├── _support.py
│   ├── test_cli.py
│   ├── test_doubly_linked_list.py
│   ├── test_hash_map.py
│   ├── test_min_heap.py
│   └── test_store.py
├── scripts/check_forbidden_builtins.py
├── docs/
│   ├── requirements.md
│   ├── testing.md
│   ├── learning.md
│   └── review.md
└── evidence/
    ├── test-results.txt
    └── repl-transcript.txt
```

## 9. Engineering / Agent Routing Result

- Orchestrator / Integrator: `ChatGPT`
- Primary Builder: `ChatGPT in current repository harness`
- Self Review: `1 completed`
- External Independent Reviewer: `NOT AVAILABLE IN CURRENT HARNESS`
  - no false Codex/Copilot review claim was made
- Specialist Agents: `OFF` — no escalation trigger
- Human Runtime: `NOT REQUIRED` for this CLI because the actual Python process and REPL were executable inside the Workcell harness

Fusion order used:

`Source → Reproducible Test → Runtime → Evidence → Finding`

Review record: `docs/review.md`

## 10. Test Result

Actual commands:

```bash
python3 -m compileall -q src main.py tests
python3 -m unittest discover -s tests -v
python3 scripts/check_forbidden_builtins.py
```

Actual result:

- compileall: `PASS`
- unit tests: `21/21 PASS`
- forbidden built-in scan: `PASS`

Coverage includes DLL invariants, hash collisions, resize, heap ordering, all commands, LRU, UTF-8 memory accounting, OOM, TTL countdown/expiration, overwrite reset, DEL consistency, passive expiry in DBSIZE/KEYS, quoted values, and error cases.

Evidence: `evidence/test-results.txt`

## 11. Runtime Result

Actual interactive CLI execution verified:

- maxmemory setup
- 3 SETs and LRU eviction
- evicted GET -> `(nil)`
- `INFO memory` -> `used_memory:22`, `maxmemory:25`, `evicted_keys:1`
- KEYS result
- EXPIRE 3 seconds + real wait + TTL countdown
- expired GET -> `(nil)` and TTL -> `-2`
- integer, wrong-args, unknown-command errors
- quit

Evidence: `evidence/repl-transcript.txt`

## 12. Evidence / Learning

| Item | Location | Status |
|---|---|---|
| test log | `evidence/test-results.txt` | PASS |
| REPL transcript | `evidence/repl-transcript.txt` | PASS |
| requirements mapping | `docs/requirements.md` | PASS |
| review | `docs/review.md` | PASS |
| learning explanations | `docs/learning.md` | PASS |
| human handoff | `HANDOFF.md` | PASS |
| machine result | `mission-result.yaml` | PASS |

Learning content G7 is complete. Human learner mastery is **not** claimed; `mission-result.yaml` intentionally keeps learning status separate as `NOT-STUDIED`.

## 13. Review Result

- BLOCKER: `0`
- MAJOR: `0`
- Secret exposure: `0`
- Outstanding required gap: `0`

Resolved during review:

- added direct test for passive expiry in `DBSIZE`/`KEYS`
- strengthened AST checker to detect dict/set literals and comprehensions as well as calls/imports

Optional backlog only:

- high-volume TTL overwrite can accumulate lazy stale heap records; a rebuild strategy is a future optimization, not a B3-1 PASS condition

## 14. Dependency / Drift

- Upstream Dependency: `NONE`
- Cross-Mission Conflict: `NONE`
- Control Tower Drift: `FOUND / NON-BLOCKING`
- Source Drift: `NONE`

## 15. Completion Gates

| Gate | Exit Condition | Status |
|---|---|---|
| G1 SOURCE | Source state/mode/gap/provenance confirmed | `PASS` |
| G2 BUILD | required implementation exists | `PASS` |
| G3 TEST | automated verification passed | `PASS` |
| G4 REVIEW | BLOCKER=0, MAJOR=0 | `PASS` |
| G5 RUNTIME | actual CLI runtime verified | `PASS` |
| G6 EVIDENCE | required actual evidence complete | `PASS` |
| G7 LEARN | code-aligned learning material complete | `PASS` |
| G8 MERGE | PR #1 merged and Handoff/result left in Mission Repository | `PASS` |

## 16. STOP Rule Result

All Mission completion conditions are met:

- required Mission requirements: PASS
- Evaluation mapping: PASS
- tests: PASS
- runtime: PASS
- evidence: PASS
- BLOCKER: 0
- MAJOR: 0
- PR: MERGED
- Handoff/result: present

**B3-1 Workcell STOP condition reached. No optional bonus implementation or further review loop is required.**

## 17. Representative Integration Contract

The Workcell does **not** edit the Control Tower.

Serial integration should read:

- `HANDOFF.md`
- `mission-result.yaml`
- PR #1 / final Mission commit
- tests/evidence

and only update the Control Tower when the representative integration order reaches B3-1.
