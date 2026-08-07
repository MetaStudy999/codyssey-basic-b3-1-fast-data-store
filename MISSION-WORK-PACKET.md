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
- Drift 판정: `FOUND / NON-BLOCKING`
  - baseline 이후 변경은 Active Wave/launcher/governance 안내 보강이며 B3-1 Mission 요구를 변경하지 않는다.
  - Action: `CONTINUE_WITH_FROZEN_BASELINE`

### Required Control Tower Context

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

- `MetaStudy999/codyssey-basic-b3-1-fast-data-store`의 `mission/b3-1` 브랜치만

### DO NOT WRITE

- `MetaStudy999/codyssey-basic`
- 다른 Mission Repository

## 4. Source Inventory

| Source Candidate | Type | State | Location | Notes |
|---|---|---|---|---|
| Mission | PDF | `VALID` | `b3-1-mission.pdf` | 8쪽 원본 Mission. 기능/제약/예시 확인 가능 |
| Mission | Markdown | `DUPLICATE` | `b3-1-mission.md` | PDF 내용을 Markdown으로 구조화한 파생본 |
| Evaluation | Markdown | `VALID` | `b3-1-evaluation.md` | 기능/자료구조/LRU·TTL·메모리/확장 사고 평가 문항 포함 |
| Official operation context | Markdown | `VALID` | frozen Control Tower governance | Gate/Source/병렬 실행 규칙만 적용 |

- Source Mode: `FULL SOURCE`
- Source Confidence: `HIGH`
- Source Gaps:
  - 별도 Evaluation PDF는 발견되지 않았으나 Evaluation Markdown은 실질 평가 문항을 완전하게 포함한다.
  - Blocking Source Gap: `NONE`

## 5. Mission Contract

### Goal

내장 Key-Value 컬렉션으로 핵심 저장 구조를 대체하지 않고 Hash Map, Doubly Linked List, Min Heap을 직접 구현하여 CLI 기반 Mini Redis의 LRU, TTL, memory limit 동작을 재현한다.

### Required Deliverables

- [ ] Python CLI Mini Redis 프로그램
- [ ] Hash Map / Doubly Linked List / Min Heap 독립 구현
- [ ] 자동 테스트
- [ ] README 실행/구조 설명
- [ ] 실제 테스트 및 REPL Evidence
- [ ] 학습 문서
- [ ] `HANDOFF.md`, `mission-result.yaml`

### Required Functions / Behaviors

- [ ] `SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS`
- [ ] `CONFIG SET maxmemory`, `INFO memory`
- [ ] `EXPIRE`, `TTL`
- [ ] `mini-redis>` REPL, `exit`/`quit`
- [ ] Redis-style 성공/정수/nil/error 출력
- [ ] Hash Map 자체 hash function + chaining + load factor 0.75 초과 시 2배 resize
- [ ] Doubly Linked List의 핵심 삽입/삭제/이동 연산 O(1)
- [ ] Min Heap의 push/pop/peek/size + heapify up/down
- [ ] `SET`/성공한 `GET` 시 LRU 갱신
- [ ] 만료된 `GET`은 삭제 후 `(nil)`, LRU 미갱신
- [ ] overwrite `SET`은 기존 TTL 초기화
- [ ] `DEL`은 data/LRU/TTL active state 동시 제거
- [ ] 공식 `used_memory = Σ(len(utf8(key)) + len(utf8(value)))`
- [ ] maxmemory 초과 시 LRU eviction 및 `evicted_keys` 증가
- [ ] 단일 엔트리 자체가 maxmemory를 초과하면 저장하지 않고 OOM
- [ ] TTL: 없는 key `-2`, TTL 없음 `-1`, 정상 TTL `N`
- [ ] 잘못된 명령/인자/정수/OOM 오류 표준 출력

### Constraints

- Python 3.8+
- `dict`, `set`, `collections`로 핵심 자료구조를 대체하지 않는다.
- 고정 배열/인덱스 접근 수준의 `list` 사용은 허용하되 Hash Map/Cache를 내장 컬렉션으로 대체하지 않는다.
- 각 핵심 자료구조는 독립 모듈로 분리한다.
- 핵심 클래스/함수에 docstring 또는 주석을 둔다.

### Explicit Non-scope

- 네트워크 통신
- 파일 영속성
- Redis List/Set/Sorted Set
- 멀티스레딩/락
- 보너스 동적 배열/스택·큐·덱/BST/PubSub

## 6. Requirement Traceability

| ID | Requirement | Source | Location | Confidence | Planned implementation | Planned test/evidence | Status |
|---|---|---|---|---|---|---|---|
| REQ-B3-1-001 | 6개 String 명령 | Mission PDF/MD | 기능 요구 2 | HIGH | `MiniRedis` + CLI | unit/CLI transcript | TODO |
| REQ-B3-1-002 | maxmemory/INFO memory | Mission PDF/MD | 기능 요구 3 | HIGH | memory accounting | unit/CLI transcript | TODO |
| REQ-B3-1-003 | EXPIRE/TTL | Mission PDF/MD | 기능 요구 4 | HIGH | heap + ttl index | fake-clock tests | TODO |
| REQ-B3-1-004 | REPL 및 오류 표준 | Mission PDF/MD | 기능 요구 5 | HIGH | `CommandProcessor`/REPL | parser tests/transcript | TODO |
| REQ-B3-1-005 | Doubly Linked List 직접 구현/O(1) | Mission PDF/MD | 기능 요구 1 | HIGH | `doubly_linked_list.py` | invariant tests | TODO |
| REQ-B3-1-006 | Hash Map hash/chaining/resize | Mission PDF/MD | 기능 요구 1 | HIGH | `hash_map.py` | collision/resize tests | TODO |
| REQ-B3-1-007 | Min Heap 직접 구현 | Mission PDF/MD | 기능 요구 1 | HIGH | `min_heap.py` | ordering/boundary tests | TODO |
| REQ-B3-1-008 | LRU + eviction | Mission PDF/MD | 기능 요구 3 | HIGH | DLL node stored in entry | deterministic tests | TODO |
| REQ-B3-1-009 | TTL/LRU edge cases | Mission PDF/MD | 기능 요구 4 | HIGH | active TTL map + lazy heap invalidation | overwrite/delete/expired GET tests | TODO |
| REQ-B3-1-010 | built-in KV replacement prohibition | Mission PDF/MD | 제약 사항 | HIGH | no dict/set/collections in `src` | static source scan | TODO |
| REQ-B3-1-011 | 구조 분리/docstring | Mission PDF/MD | 제약 사항 | HIGH | modules + docs | repository inspection | TODO |
| REQ-B3-1-012 | 학습자가 구조/복잡도 설명 가능 | Mission/Evaluation | 과제 목표/항목 2~4 | HIGH | `docs/learning.md` | explanation mapping | TODO |

## 7. Evaluation Mapping

| Evaluation ID | Criterion | Related Requirement | Validation | Evidence | Status |
|---|---|---|---|---|---|
| EVA-B3-1-01 | 기본 6명령 정상 | 001 | unit + CLI | test log/transcript | TODO |
| EVA-B3-1-02 | LRU eviction | 002,008 | deterministic unit | test log/transcript | TODO |
| EVA-B3-1-03 | INFO memory | 002 | unit + CLI | transcript | TODO |
| EVA-B3-1-04 | EXPIRE/TTL | 003,009 | fake-clock unit | test log/transcript | TODO |
| EVA-B3-1-05 | 표준 오류 | 004 | parser/OOM unit | test log/transcript | TODO |
| EVA-B3-1-06 | DLL O(1) 구조 설명 | 005,012 | code + learning doc | `docs/learning.md` | TODO |
| EVA-B3-1-07 | hash/chaining/resize 설명 | 006,012 | code + learning doc | `docs/learning.md` | TODO |
| EVA-B3-1-08 | LRU/TTL/memory/GET 흐름 설명 | 008,009,012 | code + learning doc | `docs/learning.md` | TODO |
| EVA-B3-1-09 | LFU/100k/overhead 확장 사고 | 012 | learning section | `docs/learning.md` | TODO |

## 8. Repository Baseline

- Default Branch: `main`
- Mission Repository Baseline Commit: `f62cdc0658ba9b7f6e815124804e8ff817458859`
- Work Branch: `mission/b3-1`
- Runtime / Language: Python 3.8+
- Dependency Manager: standard library only
- Existing Tests: `NO`

### Repository Inventory at G1

```text
.
├── README.md
├── b3-1-evaluation.md
├── b3-1-mission.md
└── b3-1-mission.pdf
```

### Existing Implementation

- 이미 충족: Mission/Evaluation source files
- 부분 충족: README source links
- 누락: source code, tests, runtime/evidence, learning, handoff
- 잘못 구현: `NONE` (기존 구현 자체가 없음)

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

## 10. Engineering Plan

### Prompt Engineering

- ROLE: primary B3-1 builder + integrator
- GOAL: official Mission/Evaluation minimum sufficient implementation
- SCOPE: B3-1 repo only
- OUTPUT CONTRACT: code + tests + evidence + learning + handoff
- STOP CONDITION: required items pass, BLOCKER=0, MAJOR=0, PR merged

### Context Engineering

현재 Gate에 직접 필요한 Mission/Evaluation, source code, tests만 사용한다.

### Harness Engineering

- Git boundary: `mission/b3-1`
- Test commands:
  - `python -m unittest discover -s tests -v`
  - `python -m compileall -q src main.py tests`
  - source scan for forbidden KV replacements
- Secret boundary: secret/API key 없음; credential 추가 금지
- Evidence boundary: 실제 실행 결과만 `evidence/`에 기록

### Loop Engineering

- Self review: 1회
- Independent review: 1회가 원칙. 별도 reviewer harness가 없으면 그 사실을 명시하고 Source/Test 중심으로 보수적으로 판정한다.
- Re-validation: BLOCKER/MAJOR 수정 범위만

### Fusion Engineering

`Source → Reproducible Test → Runtime → Evidence → Finding`

## 11. Agent Routing

- Orchestrator / Integrator: `ChatGPT`
- Primary Builder: `ChatGPT in current repository harness`
- Independent Reviewer: `CONDITIONAL / harness availability`
- Claude: `OFF`
- Gemini: `OFF` (PDF는 텍스트/페이지가 명확하여 specialist trigger 없음)
- Grok: `OFF`
- Runtime Authority: `ChatGPT-executed local Python runtime`; human only if local environment-specific check becomes necessary

## 12. Dependency / Drift Check

- Upstream Dependency: `NONE`
- Related Mission: `NONE`
- Control Tower Drift: `FOUND / NON-BLOCKING`
- Source Drift: `NONE at G1`
- Action: `CONTINUE`

## 13. Test Plan

| Test | Requirement | Method | Expected | Status |
|---|---|---|---|---|
| DLL invariants | 005 | unit | links/head/tail/order correct | TODO |
| Hash collision | 006 | unit | colliding keys preserved | TODO |
| Hash resize | 006 | unit | capacity doubles >0.75, data preserved | TODO |
| Heap ordering | 007 | unit | pop ascending, empty boundaries safe | TODO |
| String commands | 001 | unit | Redis-style results | TODO |
| LRU eviction | 002,008 | unit | oldest key evicted, count/memory correct | TODO |
| TTL countdown/expiry | 003,009 | fake clock | N → expired/-2 | TODO |
| overwrite TTL reset | 009 | fake clock | TTL becomes -1 | TODO |
| DEL consistency | 009 | unit | data/LRU/active TTL removed | TODO |
| CLI errors/quotes | 004 | unit + transcript | standard errors, quoted value accepted | TODO |
| forbidden built-in KV scan | 010 | static scan | no dict/set/collections replacement | TODO |

## 14. Runtime Plan

| Runtime Check | AI 가능 | Human 필요 | Evidence | Status |
|---|---|---|---|---|
| Python unit/integration tests | YES | NO | `evidence/test-results.txt` | TODO |
| Interactive REPL scenario | YES | NO | `evidence/repl-transcript.txt` | TODO |

## 15. Evidence Plan

| Evidence | Requirement / Evaluation | Capture Method | Location | Status |
|---|---|---|---|---|
| automated test log | all functional | actual test stdout/stderr | `evidence/test-results.txt` | TODO |
| REPL transcript | command/output/eviction/TTL/errors | actual stdin session | `evidence/repl-transcript.txt` | TODO |
| learning explanation | evaluation 2~4 | code-linked document | `docs/learning.md` | TODO |

## 16. Completion Gates

| Gate | Exit Condition | Status |
|---|---|---|
| G1 SOURCE | Source state/mode/gap/provenance confirmed | `PASS` |
| G2 BUILD | required implementation exists | `TODO` |
| G3 TEST | required automated tests pass | `TODO` |
| G4 REVIEW | BLOCKER=0, MAJOR=0 | `TODO` |
| G5 RUNTIME | actual CLI/runtime checks complete | `TODO` |
| G6 EVIDENCE | required Evidence complete | `TODO` |
| G7 LEARN | evaluation explanations complete | `TODO` |
| G8 MERGE | Mission PR merged | `TODO` |

## 17. STOP Rule

아래가 모두 충족되면 미션 완료를 위한 추가 구현·검토를 중단한다.

- 공식 필수 Requirement 충족
- Evaluation 항목 충족
- BLOCKER=0
- MAJOR=0
- 필수 Test 통과
- Runtime 완료
- Evidence 완료
- G8 MERGE 완료

선택 보너스와 고도화는 현재 Mission PASS를 지연시키지 않는다.

## 18. Handoff Contract

Mission 종료 시 B3-1 Repository에 다음을 남긴다.

- `HANDOFF.md`
- `mission-result.yaml`

Control Tower Repository는 이 Workcell에서 수정하지 않는다.
