# Codyssey Basic B3-1 — Mini Redis 구축

## 현재 훈련 상태

- 구분: **필수 미션 (REQUIRED)**
- Round: **R01 — CLEAR**
- Mission 상태: **⬜ NOT STARTED**
- 현재 모드: **Phase A — REFERENCE BUILD**
- Reference 판정: **CORE READY**

공식 Mission/Evaluation을 기준으로 Reference Complete Version과 자체감사를 마쳤습니다. 실제 REPL 실행·자동 검증·Evidence를 확인하기 전에는 `✅ CLEAR`로 판정하지 않습니다.

## 공식 원본

- `b3-1-mission.pdf`
- `b3-1-mission.md`
- `b3-1-evaluation.md`

공식 원본은 수정하지 않습니다.

## 시작 위치

- `training/round-01-clear/REFERENCE-BUILD.md`
- `training/round-01-clear/REFERENCE-STATUS.md`
- `training/round-01-clear/BEGINNER-GUIDE.md`
- `training/round-01-clear/CHECKLIST.md`
- `training/round-01-clear/reference/README.md`

## Reference 구현

```text
training/round-01-clear/reference/
├── main.py
├── mini_redis/
│   ├── __init__.py
│   ├── doubly_linked_list.py
│   ├── hash_map.py
│   ├── min_heap.py
│   ├── store.py
│   └── cli.py
└── tests/
    └── test_mini_redis.py
```

핵심 자료구조는 직접 구현합니다.

- Doubly Linked List — LRU 순서
- Chaining HashMap — key/value 조회
- MinHeap — TTL 만료 후보

핵심 저장소 구현에서 `dict`, `set`, `collections`, `heapq`를 사용하지 않습니다.

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

명령:

```text
SET key value
GET key
DEL key
EXISTS key
DBSIZE
KEYS
CONFIG SET maxmemory bytes
INFO memory
EXPIRE key seconds
TTL key
```

종료:

```text
exit
quit
```

## 검증

Reference 검증:

```bash
bash training/round-01-clear/environment/verify.sh
```

Phase C Runtime Evidence까지 준비한 뒤:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```

Reference verifier는 다음을 확인하도록 강화했습니다.

- Python 3.8+
- AST syntax parse
- 전체 unit tests
- `dict/set/collections/heapq` 금지 AST 검사
- String/OOM smoke test
- tracked Secret-pattern 파일 부재
- Runtime 모드에서 실제 Evidence 3종과 REPL command/error coverage

## 자체감사에서 강화한 핵심

- DLL 필수 6개 연산 테스트
- 실제 chaining collision 테스트
- load factor `0.75` 유지 / `>0.75` resize 경계
- MinHeap push/pop/peek/size
- `maxmemory=0` unlimited
- UTF-8 overwrite memory accounting
- GET과 SET overwrite 모두 LRU refresh
- oversized entry OOM 시 기존 데이터/evicted count 보존
- 제한 이하까지 반복 LRU eviction
- EXPIRE 재설정 lazy deletion
- DEL 후 동일 key 재삽입 stale TTL 안전성
- SET overwrite stale TTL 무효화
- expired key의 GET/EXISTS/DEL/TTL/DBSIZE/KEYS 의미
- LFU 전환, 10만 건 병목, 메모리 overhead 모델, 채점 보정 Q&A

## 공식 핵심 규칙

- `used_memory = Σ(len(utf8(key)) + len(utf8(value)))`
- `maxmemory=0`은 무제한
- 제한 초과 시 LRU부터 제거
- 단일 entry 자체가 maxmemory보다 크면 OOM
- 성공한 SET/GET만 LRU 갱신
- SET overwrite 시 기존 TTL 초기화
- TTL: key 없음 `-2`, TTL 없음 `-1`, 남은 시간 `N`
- `EXPIRE <= 0`은 즉시 삭제

## 문서

- `REFERENCE-STATUS.md` — Phase A 자체감사/판정
- `docs/requirements-mapping.md` — 공식 요구와 구현/검증/Evidence 연결
- `docs/evaluation-qa.md` — 자료구조·LRU·TTL·확장 사고 평가 설명 기준
- `evidence/README.md` — 실제 Runtime Evidence 계획

## CLEAR 원칙

Reference 코드와 unit test가 작성되었다는 사실만으로 CLEAR하지 않습니다. Phase C에서 실제 REPL, LRU/OOM/TTL edge case, 실제 시간 경과, verify 결과, Evidence와 설명형 평가를 확인한 뒤 `✅ CLEAR`로 변경합니다.
