# B3-1 R01 — Reference Build

## 목적

공식 Mission/Evaluation을 기준으로 내장 `dict`, `set`, `collections`로 핵심 저장소를 대체하지 않고 **이중 연결 리스트 + 체이닝 해시맵 + 최소 힙**을 직접 구현한 CLI Mini Redis 기준본을 준비합니다.

Reference Build가 완료되어도 Phase C에서 실제 REPL/테스트/Evidence를 확인하기 전에는 `✅ CLEAR`로 판정하지 않습니다.

## Source of Truth

1. `b3-1-mission.pdf`
2. `b3-1-mission.md`
3. `b3-1-evaluation.md`

## Reference 설계 결정

- Python 3.8+ 호환
- `dict`, `set`, `collections`, `heapq`로 핵심 자료구조 대체 금지
- Python `list`는 버킷 배열/힙 배열 등 인덱스 기반 저장소로 사용
- 해시맵: 직접 hash 함수 + chaining + load factor `> 0.75` + 2배 resize
- LRU: HashMap Entry가 DoublyLinkedList node를 직접 참조해 성공 GET/SET에서 O(1) move-to-front
- TTL: 직접 구현 MinHeap + Entry `expire_at`/`ttl_version` lazy deletion
- `used_memory`: 공식 UTF-8 key bytes + value bytes만 합산
- 단일 entry 자체가 maxmemory 초과 시 기존 데이터 eviction 없이 OOM
- 기존 SET overwrite 시 TTL 초기화
- key 기반 명령에서 만료를 먼저 처리
- CLI parsing: `shlex.split()`으로 quoted value 지원

## Reference Complete Path

1. 자료구조 3종 구현/테스트
2. MiniRedis store
3. String 6 commands
4. maxmemory/INFO
5. LRU eviction
6. EXPIRE/TTL
7. TTL/LRU/OOM edge cases
8. Redis-style error standard
9. REPL
10. 자동 verify
11. Evaluation Q&A
12. Runtime Evidence
13. CLEAR

## Reference Build 준비 결과

- [x] Source/Evaluation 분석
- [x] Doubly Linked List 직접 구현
- [x] Chaining HashMap 직접 구현
- [x] MinHeap 직접 구현
- [x] HashMap load factor `0.75` 경계 / `>0.75` 2배 resize
- [x] 실제 chaining collision test
- [x] String 6 commands
- [x] `CONFIG SET maxmemory`
- [x] `INFO memory`
- [x] UTF-8 공식 memory 계산식
- [x] O(1) LRU 구조
- [x] GET 및 SET-overwrite LRU refresh test
- [x] single-entry OOM + 기존 데이터 보존 test
- [x] 반복 eviction으로 limit 복귀 test
- [x] EXPIRE/TTL
- [x] EXPIRE 재설정 lazy deletion test
- [x] DEL 후 같은 key 재삽입 stale TTL test
- [x] SET overwrite TTL reset/stale item test
- [x] expired-key command semantics test
- [x] REPL / quoted parsing / Redis-style errors
- [x] unit test 기준본 강화
- [x] `dict/set/collections/heapq` AST 검사
- [x] AST syntax parse로 verify 부작용 최소화
- [x] tracked Secret-pattern scan
- [x] Runtime Evidence 전용 `verify.sh --runtime`
- [x] `reference/README.md`
- [x] `BEGINNER-GUIDE.md` Step 01~08
- [x] `CHECKLIST.md`
- [x] Requirement Mapping 31개 항목
- [x] Evaluation Q&A — LFU/10만 건/overhead/채점 보정 포함
- [x] Evidence Guide
- [x] `REFERENCE-STATUS.md` 자체감사
- [x] 실제 Runtime 결과를 PASS로 표시하지 않음

## 자체감사 핵심 보완

### 자료구조 정확성

- DLL 필수 6개 메서드를 모두 실제 unit test 대상으로 포함
- HashMap은 resize만 확인하지 않고 **실제 same-bucket collision**을 만들어 chaining 보존 확인
- 공식 문구 그대로 load factor가 `0.75를 초과`할 때만 resize되는 경계를 test
- MinHeap의 push/pop/peek/size와 정렬 순서를 함께 확인

### LRU / Memory

- `maxmemory=0` unlimited 확인
- UTF-8 overwrite 시 used_memory 재계산 확인
- 성공 GET뿐 아니라 SET overwrite도 MRU가 되는지 확인
- oversized single entry가 OOM이어도 기존 데이터와 `evicted_keys`를 보존
- memory 초과 시 한 번이 아니라 제한 이하까지 반복 eviction 확인

### TTL

- EXPIRE 재설정 시 오래된 heap item이 현재 TTL을 삭제하지 않는지 검증
- DEL 후 동일 key 재삽입 시 과거 TTL이 새 데이터를 삭제하지 않는지 검증
- overwrite 후 기존 TTL heap item이 stale 처리되는지 검증
- GET/EXISTS/DEL/TTL/DBSIZE/KEYS에서 만료 데이터 의미를 일관되게 검증

### Evaluation Coverage

공식 평가의 확장 사고까지 기준 답안을 보완했습니다.

- LRU → LFU 전환 구조
- 10만 건 병목과 개선
- 자료구조 overhead 포함 memory model
- 서로 다른 구현을 공정하게 비교하기 위한 채점 보정 기준

## Phase C에서 확인할 것

- [ ] Python 3.8+ 실제 환경
- [ ] `environment/verify.sh` 실제 실행 0 FAIL
- [ ] 기본 REPL 명령 실제 확인
- [ ] LRU GET/SET-overwrite sequence 실제 확인
- [ ] single-entry OOM + 기존 key 유지 실제 확인
- [ ] UTF-8 `used_memory` 실제 확인
- [ ] TTL 실제 시간 경과 확인
- [ ] EXPIRE 재설정 / 즉시 만료 / overwrite TTL reset 확인
- [ ] 오류 command 실제 확인
- [ ] `evidence/runtime/` 실제 Evidence
- [ ] `verify.sh --runtime` 0 FAIL
- [ ] 사용자 자기 말 Evaluation 설명
- [ ] `✅ B3-1 CLEAR`

## 현재 판정

**Reference Build: CORE READY**

**Mission 상태: ⬜ NOT STARTED 유지 / Runtime 미시작 / CLEAR 아님**

다음 Phase A 작업은 **B3-2 자체감사/정합성 마감**입니다.
