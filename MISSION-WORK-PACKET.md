# B3-1 Mission Work Packet — Mini Redis

> 확정일: 2026-08-08  
> 이 Workcell은 `MetaStudy999/codyssey-basic`을 READ ONLY로 사용하고, B3-1 저장소만 수정한다.

## 1. Identity

- Mission ID: `B3-1`
- Mission Title: 정보를 엄청 빠르게 찾아주는 작은 저장소 만들기
- Mission Repository: `MetaStudy999/codyssey-basic-b3-1-fast-data-store`
- Workcell: `Chat 5 / B3-1`
- Started At: `2026-08-08T04:36:00+09:00`

## 2. Control Tower Baseline

- Control Tower Repository: `MetaStudy999/codyssey-basic`
- Frozen Baseline SHA: `0d1581b3e82366988f57e1d76da311c028b8e15e`
- Current Control Tower main observed at G1: `f6192ad701bd1d2c317f908d210e7049f6b32310`
- Baseline Rule: Workcell 판단은 frozen baseline을 유지한다.
- Drift: `FOUND / NON-BLOCKING`
  - baseline 이후 변경은 Active Wave/launcher/governance 안내 보강이며 B3-1 Mission 요구를 변경하지 않는다.
  - Action: `CONTINUE_WITH_FROZEN_BASELINE`

### Required Control Tower Context read

- `AGENTS.md`
- `docs/00-governance/multi-agent-mission-engineering.md`
- `docs/00-governance/source-discovery-fallback-protocol.md`
- `docs/00-governance/parallel-mission-execution.md`
- `docs/00-governance/work-packets/b3-1.md`
- `config/waves/20260808-01.yaml`

## 3. Read / Write Boundary

### READ

- Control Tower frozen baseline
- 현재 B3-1 Repository
- B3-1 Mission/Evaluation Source

### WRITE

- `MetaStudy999/codyssey-basic-b3-1-fast-data-store`만
- 구현 작업 브랜치: `mission/b3-1`

### DO NOT WRITE

- `MetaStudy999/codyssey-basic`
- 다른 Mission Repository

## 4. Source Inventory

| Source Candidate | Type | State | Location | Notes |
|---|---|---|---|---|
| Mission | PDF | `VALID` | `b3-1-mission.pdf` | 8쪽 원본 Mission |
| Mission | Markdown | `DUPLICATE` | `b3-1-mission.md` | PDF 내용을 Markdown으로 구조화한 파생본 |
| Evaluation | Markdown | `VALID` | `b3-1-evaluation.md` | 기능/구조/LRU·TTL·메모리/확장 사고 평가 |
| Official operation context | Markdown | `VALID` | frozen Control Tower governance | Gate/Source/병렬 실행 규칙 |

- Source Mode: `FULL SOURCE`
- Source Confidence: `HIGH`
- Source Gaps:
  - 별도 Evaluation PDF는 발견되지 않았으나 Evaluation Markdown은 실질 평가 문항을 포함한다.
  - Blocking Source Gap: `NONE`

## 5. Mission Contract

### Goal

내장 Key-Value 컬렉션으로 핵심 저장 구조를 대체하지 않고 Hash Map, Doubly Linked List, Min Heap을 직접 구현하여 CLI 기반 Mini Redis의 LRU, TTL, memory limit 동작을 재현한다.

### Required Deliverables

- [x] Python CLI Mini Redis 프로그램
- [x] Hash Map / Doubly Linked List / Min Heap 독립 구현
- [x] 자동 테스트
- [x] README 실행/구조 설명
- [x] 실제 테스트 및 REPL Evidence
- [x] 학습 문서
- [ ] `HANDOFF.md`, `mission-result.yaml` — G8 PR/merge metadata 확정 시 작성

### Required Functions / Behaviors

- [x] `SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS`
- [x] `CONFIG SET maxmemory`, `INFO memory`
- [x] `EXPIRE`, `TTL`
- [x] `mini-redis>` REPL, `exit`/`quit`
- [x] Redis-style 성공/정수/nil/error 출력
- [x] Hash Map 자체 hash function + chaining + load factor 0.75 초과 시 2배 resize
- [x] Doubly Linked List의 핵심 삽입/삭제/이동 연산 O(1)
- [x] Min Heap의 push/pop/peek/size + heapify up/down
- [x] `SET`/성공한 `GET` 시 LRU 갱신
- [x] 만료된 `GET`은 삭제 후 `(nil)`, LRU 미갱신
- [x] overwrite `SET`은 기존 TTL 초기화
- [x] `DEL`은 data/LRU/active TTL 동시 제거
- [x] 공식 `used_memory = Σ(len(utf8(key)) + len(utf8(value)))`
- [x] maxmemory 초과 시 LRU eviction 및 `evicted_keys` 증가
- [x] 단일 엔트리 자체가 maxmemory를 초과하면 저장하지 않고 OOM
- [x] TTL: 없는 key `-2`, TTL 없음 `-1`, 정상 TTL `N`
- [x] 잘못된 명령/인자/정수/OOM 오류 표준 출력

### Constraints

- Python 3.8+ — actual runtime `Python 3.13.5`
- `dict`, `set`, `collections`로 핵심 자료구조를 대체하지 않음
- `list`는 배열/heap/bucket table 결과 표현에 사용하되 KV 저장소 대체에 사용하지 않음
- 핵심 자료구조를 독립 모듈로 분리함
- 핵심 클래스/함수에 docstring 또는 설명을 둠

### Explicit Non-scope

- 네트워크 통신
- 파일 영속성
- Redis List/Set/Sorted Set
- 멀티스레딩/락
- 선택 보너스: 동적 배열 직접 구현, 스택/큐/덱, BST, Pub/Sub

## 6. Requirement Traceability

| ID | Requirement | Implementation | Validation / Evidence | Status |
|---|---|---|---|---|
| REQ-B3-1-001 | 6개 String 명령 | `store.py`, `cli.py` | unit + REPL | PASS |
| REQ-B3-1-002 | maxmemory/INFO memory | `store.py` | memory/LRU tests + REPL | PASS |
| REQ-B3-1-003 | EXPIRE/TTL | heap + active TTL map | fake-clock + real REPL | PASS |
| REQ-B3-1-004 | REPL 및 오류 표준 | `CommandProcessor` | parser tests + transcript | PASS |
| REQ-B3-1-005 | DLL 직접 구현/O(1) | `doubly_linked_list.py` | invariant tests + learning | PASS |
| REQ-B3-1-006 | Hash Map hash/chaining/resize | `hash_map.py` | collision/resize tests | PASS |
| REQ-B3-1-007 | Min Heap 직접 구현 | `min_heap.py` | ordering/boundary tests | PASS |
| REQ-B3-1-008 | LRU + eviction | Entry -> DLL node | deterministic tests | PASS |
| REQ-B3-1-009 | TTL/LRU edge cases | lazy heap + active TTL map | overwrite/delete/expired/purge tests | PASS |
| REQ-B3-1-010 | built-in KV replacement 금지 | custom structures | AST static scan | PASS |
| REQ-B3-1-011 | 구조 분리/docstring | independent modules | repository review | PASS |
| REQ-B3-1-012 | 구조/복잡도/확장 설명 | `docs/learning.md` | evaluation mapping | PASS |

## 7. Evaluation Mapping

| Evaluation ID | Criterion | Validation | Evidence | Status |
|---|---|---|---|---|
| EVA-B3-1-01 | 기본 6명령 정상 | unit + CLI | test results / transcript | PASS |
| EVA-B3-1-02 | LRU eviction | deterministic unit + REPL | test results / transcript | PASS |
| EVA-B3-1-03 | INFO memory | unit + CLI | transcript | PASS |
| EVA-B3-1-04 | EXPIRE/TTL | fake-clock + real wait | test results / transcript | PASS |
| EVA-B3-1-05 | 표준 오류 | CLI tests | test results / transcript | PASS |
| EVA-B3-1-06 | DLL O(1) 설명 | code-linked explanation | `docs/learning.md` | PASS |
| EVA-B3-1-07 | hash/chaining/resize 설명 | code-linked explanation | `docs/learning.md` | PASS |
| EVA-B3-1-08 | LRU/TTL/memory/GET 흐름 설명 | code-linked explanation | `docs/learning.md` | PASS |
| EVA-B3-1-09 | LFU/100k/overhead/채점 보정 | extension explanation | `docs/learning.md` | PASS |

## 8. Repository Baseline / Result Structure

- Default Branch: `main`
- Mission Repository Baseline Commit: `f62cdc0658ba9b7f6e815124804e8ff817458859`
- Work Branch: `mission/b3-1`
- Runtime: Python 3.13.5 used for verification; Mission minimum is Python 3.8+
- Dependency Manager: standard library only
- Initial implementation/tests: none

### Implemented structure

```text
.
├── AGENTS.md
├── MISSION-WORK-PACKET.md
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

## 9. Mission-specific TOC

```text
B3-1 Mini Redis
├── Source / Evaluation
├── REPL / Command Parser
├── Custom Hash Map
│   ├── Hash Function
│   ├── Chaining
│   └── Resize
├── Doubly Linked List
├── LRU
├── Min Heap
├── TTL / Expiration
├── Memory Accounting
├── Eviction
├── Commands / Error Contract
├── Edge Cases
├── Tests / Evidence
├── Learning / Complexity / Extension
└── Handoff
```

## 10. Engineering / Agent Routing Result

- Orchestrator / Integrator: ChatGPT
- Primary Builder: ChatGPT in current repository harness
- Self review: 1회 완료
- Independent external reviewer: 현재 하네스에 별도 Codex/Copilot 실행 인터페이스가 없어 수행했다고 주장하지 않음
- Specialist agents: trigger 없음, 호출하지 않음
- Runtime Authority: 현재 Python/CLI 검증은 로컬 실행 가능하여 별도 Human runtime 불필요
- Review detail: `docs/review.md`

판정 순위:

`Source → Reproducible Test → Runtime → Evidence → Finding`

## 11. Dependency / Drift Check

- Upstream Dependency: `NONE`
- Related Mission: `NONE`
- Control Tower Drift: `FOUND / NON-BLOCKING`
- Source Drift: `NONE`
- Action: `CONTINUE_WITH_FROZEN_BASELINE`

## 12. Test Result

Actual commands:

```bash
python3 -m compileall -q src main.py tests
python3 -m unittest discover -s tests -v
python3 scripts/check_forbidden_builtins.py
```

Result:

- compileall: PASS
- unit tests: **21/21 PASS**
- forbidden built-in scan: PASS

Covered:

- DLL invariants / empty boundary
- hash collision / chaining / resize
- heap ordering / empty boundary
- all String commands
- LRU order / eviction
- UTF-8 memory accounting
- single-entry OOM and overwrite preservation
- TTL countdown / expiration / missing/no-TTL codes
- expired GET without LRU touch
- overwrite TTL reset / stale heap inertness
- DEL data/LRU/active-TTL consistency
- passive expiry in `DBSIZE` / `KEYS`
- quoted value / case-insensitive command
- invalid command / args / integer / negative maxmemory / OOM

Evidence: `evidence/test-results.txt`

## 13. Runtime Result

Interactive CLI was actually executed with:

- maxmemory setup
- 3 SETs causing LRU eviction
- GET evicted key -> `(nil)`
- INFO memory -> `used_memory:22`, `maxmemory:25`, `evicted_keys:1`
- KEYS
- EXPIRE 3 seconds
- real wait + TTL countdown
- expiration -> `(nil)` and TTL `-2`
- integer/wrong-args/unknown-command errors
- quit

Evidence: `evidence/repl-transcript.txt`

Human-only environment check required: `NONE`

## 14. Evidence

| Evidence | Location | Status |
|---|---|---|
| automated test log | `evidence/test-results.txt` | PASS |
| actual REPL transcript | `evidence/repl-transcript.txt` | PASS |
| learning explanation | `docs/learning.md` | PASS |
| requirement mapping | `docs/requirements.md` | PASS |
| review record | `docs/review.md` | PASS |

## 15. Review Result

- BLOCKER: 0
- MAJOR: 0
- Secret exposure: 0
- Required gap: 0
- Resolved test gaps:
  - passive expiry for DBSIZE/KEYS test added
  - forbidden built-in AST scan strengthened for literal/comprehension cases
- Backlog only:
  - high-volume TTL overwrite can accumulate lazy stale heap records; heap rebuild is an advanced optimization, not Mission PASS requirement

## 16. Completion Gates

| Gate | Exit Condition | Status |
|---|---|---|
| G1 SOURCE | Source state/mode/gap/provenance confirmed | `PASS` |
| G2 BUILD | required implementation exists | `PASS` |
| G3 TEST | required automated tests pass | `PASS` |
| G4 REVIEW | BLOCKER=0, MAJOR=0 | `PASS` |
| G5 RUNTIME | actual CLI/runtime check complete | `PASS` |
| G6 EVIDENCE | required evidence complete | `PASS` |
| G7 LEARN | evaluation explanation content complete | `PASS` |
| G8 MERGE | Mission Repository PR/merge complete | `TODO` |

## 17. STOP Rule

G8 merge 및 Handoff metadata 확정 후 다음 조건이 모두 충족되면 STOP한다.

- 공식 필수 Requirement 충족
- Evaluation 충족
- BLOCKER=0
- MAJOR=0
- Test 통과
- Runtime 완료
- Evidence 완료
- G8 MERGE 완료

선택 보너스/고도화는 현재 Mission 완료를 지연시키지 않는다.

## 18. Handoff Contract

G8에서 Mission PR/merge 정보를 확정한 뒤 B3-1 Repository에 남긴다.

- `HANDOFF.md`
- `mission-result.yaml`

Control Tower Repository는 이 Workcell에서 수정하지 않는다.
