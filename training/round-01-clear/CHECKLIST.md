# B3-1 Round 01 — Mission Clear Checklist

> Mission 상태는 `⬜ NOT STARTED`, `🟡 ACTIVE`, `⛔ BLOCKED`, `✅ CLEAR`만 사용합니다. 현재는 Phase A Reference Build이며 실제 REPL/Evidence는 Phase C에서 수행합니다.

## 현재 상태

- Training Round: **R01 — CLEAR**
- Mission: **B3-1**
- Mission 상태: **⬜ NOT STARTED**
- 작업 모드: **Phase A — REFERENCE BUILD**
- Reference 판정: **CORE READY**

## A. Source

- [x] `b3-1-mission.pdf` 확인
- [x] `b3-1-mission.md` 확인
- [x] `b3-1-evaluation.md` 확인
- [x] 필수/보너스 구분
- [x] Reference 설계 결정
- [x] `REFERENCE-STATUS.md` 자체감사 기록

## B. Data Structures

### Doubly Linked List
- [x] `prev`, `next`, `data`
- [x] `insert_front`
- [x] `insert_back`
- [x] `remove_front`
- [x] `remove_back`
- [x] `remove_node`
- [x] `move_to_front`
- [x] head/tail sentinel
- [x] Node reference 기반 O(1) 구조
- [x] 필수 6개 연산 unit test

### HashMap
- [x] 직접 hash 함수
- [x] chaining
- [x] `put/get/remove/contains/keys/size`
- [x] 실제 same-bucket collision test
- [x] load factor `== 0.75`에서는 유지
- [x] load factor `> 0.75`에서 bucket 2배 resize
- [x] resize 후 기존 key 재조회 test

### MinHeap
- [x] `push/pop/peek/size`
- [x] `_heapify_up`
- [x] `_heapify_down`
- [x] TTL item `(expire_at, version, key)`
- [x] multiple item ordering/size test

## C. 금지 자료구조

- [x] 핵심 구현 `dict` 미사용
- [x] 핵심 구현 `set` 미사용
- [x] `collections` 미사용
- [x] `heapq` 미사용
- [x] list는 bucket/heap 등 인덱스 기반 용도
- [x] AST 검증에 `dict/set/collections/heapq` 포함
- [x] verifier가 `compileall` 대신 AST parse 사용
- [ ] 실제 Runtime에서 verify 결과 PASS

## D. String Commands

- [x] SET
- [x] GET
- [x] DEL
- [x] EXISTS
- [x] DBSIZE
- [x] KEYS
- [x] 성공 GET만 LRU 갱신
- [x] 성공 SET/overwrite도 LRU 갱신
- [x] SET overwrite TTL reset
- [x] expired key를 없는 key처럼 처리
- [x] quoted string input
- [ ] Runtime 명령 실제 확인

## E. Memory / LRU

- [x] `CONFIG SET maxmemory bytes`
- [x] 0 = unlimited
- [x] 음수/정수 오류
- [x] `INFO memory`
- [x] `used_memory`
- [x] `maxmemory`
- [x] `evicted_keys`
- [x] 공식 UTF-8 key+value byte 계산
- [x] overwrite memory accounting
- [x] SET 후 제한 초과 시 LRU eviction
- [x] 제한 이하까지 반복 eviction
- [x] GET 기반 LRU 순서 test
- [x] SET overwrite 기반 LRU 순서 test
- [x] single entry > maxmemory OOM
- [x] OOM 시 기존 key 보존
- [x] OOM 실패 때문에 `evicted_keys` 증가하지 않음
- [ ] Runtime LRU/OOM/INFO Evidence

## F. TTL

- [x] EXPIRE
- [x] TTL
- [x] 없는 key EXPIRE → 0
- [x] seconds <= 0 즉시 삭제
- [x] TTL `-2/-1/N`
- [x] MinHeap 기반 만료 후보 관리
- [x] EXPIRE 재설정 lazy deletion
- [x] stale old expiration이 새 TTL을 삭제하지 않음
- [x] DEL 후 같은 key 재삽입 시 stale TTL 안전
- [x] SET overwrite 시 stale TTL 무효화
- [x] DEL/SET overwrite의 TTL 논리 무효화 설명
- [x] DBSIZE/KEYS 전 expired purge
- [x] GET/EXISTS/DEL/TTL에서 expired key 의미 test
- [ ] Runtime 실제 시간 경과 확인

## G. CLI / Errors

- [x] REPL
- [x] 명령 대소문자 무관
- [x] `exit`/`quit`
- [x] 공백 문자열 quoted parsing
- [x] wrong number of arguments
- [x] integer error
- [x] negative maxmemory error
- [x] unknown command
- [x] syntax error
- [x] OOM error
- [ ] Runtime REPL 확인

## H. Reference Tests / Verify / Docs

- [x] linked list required-method tests
- [x] hash map collision/resize boundary tests
- [x] min heap tests
- [x] String command tests
- [x] UTF-8/overwrite memory tests
- [x] LRU GET/SET tests
- [x] OOM data-preservation test
- [x] TTL reset/delete/overwrite stale-item tests
- [x] expired-key behavior tests
- [x] CLI error/quoted/repl quit tests
- [x] `environment/verify.sh`
- [x] side-effect-light AST syntax parse
- [x] tracked Secret-pattern scan
- [x] `verify.sh --runtime` Evidence gate
- [x] `reference/README.md`
- [x] `REFERENCE-STATUS.md`
- [x] `docs/requirements-mapping.md`
- [x] `docs/evaluation-qa.md`
- [x] `evidence/README.md`
- [x] `BEGINNER-GUIDE.md` Step 01~08
- [ ] Reference verify 실제 실행 0 FAIL

## I. Evaluation 설명

- [x] DLL Node/pointer와 O(1)
- [x] 직접 hash 함수 흐름
- [x] hash collision/chaining
- [x] load factor/resize 경계
- [x] O(1) LRU 핵심 구조
- [x] 성공 GET만 LRU 갱신 이유
- [x] GET 전체 처리 순서
- [x] official used_memory 식
- [x] eviction 전체 흐름
- [x] single-entry OOM 이유
- [x] overwrite memory/TTL
- [x] heap TTL 적합성
- [x] stale TTL lazy deletion
- [x] DEL 구조 일관성
- [x] LRU → LFU 변경 설계
- [x] 10만 건 병목/개선
- [x] 자료구조 overhead 포함 memory model
- [x] 공정한 비교/채점 보정 기준
- [ ] 사용자가 실제 코드/Runtime을 근거로 자기 말 설명

## J. Runtime Evidence

Phase C에서 JIT 생성:

```text
evidence/runtime/
├── verify-output.txt
├── repl-session.txt
└── evaluation-self-check.md
```

- [ ] verify 실제 결과 `0 FAIL`
- [ ] REPL 기본 6 commands
- [ ] LRU GET sequence
- [ ] LRU SET-overwrite sequence
- [ ] OOM + 기존 key 보존
- [ ] INFO memory
- [ ] TTL 실제 시간 경과
- [ ] EXPIRE reset
- [ ] overwrite TTL reset
- [ ] error commands
- [ ] Evaluation 자기 말 정리
- [ ] Secret/credential 없음
- [ ] `verify.sh --runtime` 0 FAIL

## K. Final CLEAR

- [ ] 공식 Mission 누락 없음 Runtime 최종 확인
- [ ] 공식 Evaluation 누락 없음 Runtime 최종 확인
- [ ] unit/verify 실제 PASS
- [ ] REPL Runtime 완료
- [ ] LRU/OOM/TTL edge Runtime 완료
- [ ] 필요한 Evidence 완료
- [ ] 설명형 평가 대응 가능
- [ ] **✅ B3-1 CLEAR**

**Reference Build는 CORE READY이지만 Runtime Mission은 아직 `⬜ NOT STARTED`이며 CLEAR가 아닙니다.**
