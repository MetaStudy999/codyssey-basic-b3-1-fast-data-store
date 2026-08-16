# B3-1 Round 01 — Mission Clear Checklist

> Mission 상태는 `⬜ NOT STARTED`, `🟡 ACTIVE`, `⛔ BLOCKED`, `✅ CLEAR`만 사용합니다. 현재는 Reference Build이며 실제 REPL/Evidence는 나중에 수행합니다.

## 현재 상태

- Training Round: **R01 — CLEAR**
- Mission: **B3-1**
- Mission 상태: **⬜ NOT STARTED**
- 작업 모드: **Phase A — REFERENCE BUILD**

## A. Source

- [x] `b3-1-mission.pdf` 확인
- [x] `b3-1-mission.md` 확인
- [x] `b3-1-evaluation.md` 확인
- [x] 필수/보너스 구분
- [x] Reference 설계 결정

## B. Data Structures

### Doubly Linked List
- [x] `prev`, `next`, `data`
- [x] `insert_front`
- [x] `insert_back`
- [x] `remove_front`
- [x] `remove_back`
- [x] `remove_node`
- [x] `move_to_front`
- [x] O(1) 구조

### HashMap
- [x] 직접 hash 함수
- [x] chaining
- [x] `put/get/remove/contains/keys/size`
- [x] load factor > 0.75
- [x] bucket 2배 resize

### MinHeap
- [x] `push/pop/peek/size`
- [x] `_heapify_up`
- [x] `_heapify_down`
- [x] TTL item `(expire_at, version, key)`

## C. 금지 자료구조

- [x] 핵심 구현 `dict` 미사용
- [x] 핵심 구현 `set` 미사용
- [x] `collections` 미사용
- [x] `heapq` 미사용
- [x] list는 bucket/heap 등 인덱스 기반 용도
- [x] AST 검증을 `verify.sh`에 포함
- [ ] 실제 verify 결과 PASS

## D. String Commands

- [x] SET
- [x] GET
- [x] DEL
- [x] EXISTS
- [x] DBSIZE
- [x] KEYS
- [x] 성공 GET만 LRU 갱신
- [x] SET overwrite TTL reset
- [x] expired key를 없는 key처럼 처리
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
- [x] SET 후 제한 초과 시 LRU eviction
- [x] 제한 이하까지 반복 eviction
- [x] single entry > maxmemory OOM
- [x] OOM 시 기존 key 불필요 eviction 방지
- [ ] Runtime LRU/OOM Evidence

## F. TTL

- [x] EXPIRE
- [x] TTL
- [x] key 없음 EXPIRE 0
- [x] seconds <= 0 즉시 삭제
- [x] TTL `-2/-1/N`
- [x] MinHeap 기반 만료 후보 관리
- [x] EXPIRE 재설정 lazy deletion
- [x] DEL/SET overwrite 시 stale TTL 무효화
- [x] DBSIZE/KEYS 전 expired purge
- [ ] Runtime 실제 시간 경과 확인

## G. CLI / Errors

- [x] REPL
- [x] 명령 대소문자 무관
- [x] `exit`/`quit`
- [x] 공백 문자열 quoted parsing
- [x] wrong number of arguments
- [x] integer error
- [x] unknown command
- [x] OOM error
- [ ] Runtime REPL 확인

## H. Reference Tests / Docs

- [x] linked list tests
- [x] hash map tests
- [x] min heap tests
- [x] string commands tests
- [x] UTF-8 memory test
- [x] LRU test
- [x] OOM test
- [x] TTL/overwrite test
- [x] CLI error test
- [x] `environment/verify.sh`
- [x] `reference/README.md`
- [x] `docs/requirements-mapping.md`
- [x] `docs/evaluation-qa.md`
- [x] `evidence/README.md`
- [x] `BEGINNER-GUIDE.md` Step 01~08
- [ ] Reference verify 실제 실행 0 FAIL

## I. Evaluation 설명

- [x] SET/GET 평균 O(1) 이유
- [x] hash collision/chaining
- [x] load factor/resize
- [x] O(1) LRU 핵심 구조
- [x] 성공 GET만 LRU 갱신 이유
- [x] official used_memory 식
- [x] single-entry OOM 이유
- [x] overwrite memory/TTL
- [x] heap TTL 적합성
- [x] stale TTL lazy deletion
- [x] DEL 구조 일관성
- [x] production 개선 방향
- [ ] 사용자가 실제 코드를 근거로 자기 말 설명

## J. Evidence

- [ ] verify 실제 결과
- [ ] REPL 기본 명령
- [ ] LRU sequence
- [ ] OOM
- [ ] INFO memory
- [ ] TTL 실제 시간 경과
- [ ] overwrite TTL reset
- [ ] error commands
- [ ] Secret/credential 없음

## K. Final CLEAR

- [ ] 공식 Mission 누락 없음
- [ ] 공식 Evaluation 누락 없음
- [ ] unit/verify 실제 PASS
- [ ] REPL Runtime 완료
- [ ] LRU/OOM/TTL edge Runtime 완료
- [ ] Evidence 완료
- [ ] 설명형 평가 대응 가능
- [ ] **✅ B3-1 CLEAR**
