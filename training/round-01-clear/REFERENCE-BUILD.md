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
- 해시맵: 직접 hash 함수 + chaining + load factor 0.75 + 2배 resize
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
- [x] HashMap load factor 0.75 / 2배 resize
- [x] String 6 commands
- [x] `CONFIG SET maxmemory`
- [x] `INFO memory`
- [x] UTF-8 공식 memory 계산식
- [x] O(1) LRU 구조
- [x] single-entry OOM
- [x] EXPIRE/TTL
- [x] TTL 재설정 lazy deletion
- [x] SET overwrite TTL reset
- [x] DEL 구조 일관성
- [x] REPL / quoted parsing / Redis-style errors
- [x] unit test 기준본
- [x] 금지 자료구조 AST 검사 포함 `verify.sh`
- [x] `reference/README.md`
- [x] `BEGINNER-GUIDE.md` Step 01~08
- [x] `CHECKLIST.md`
- [x] Requirement Mapping
- [x] Evaluation Q&A
- [x] Evidence Guide
- [x] 실제 Runtime 결과를 PASS로 표시하지 않음

## Phase C에서 확인할 것

- [ ] Python 3.8+ 실제 환경
- [ ] `environment/verify.sh` 실제 실행 0 FAIL
- [ ] 기본 REPL 명령 실제 확인
- [ ] LRU sequence 실제 확인
- [ ] single-entry OOM 실제 확인
- [ ] UTF-8 `used_memory` 실제 확인
- [ ] TTL 실제 시간 경과 확인
- [ ] EXPIRE 재설정 / 즉시 만료 / overwrite TTL reset 확인
- [ ] 오류 command 실제 확인
- [ ] Runtime Evidence
- [ ] 사용자 자기 말 Evaluation 설명
- [ ] `✅ B3-1 CLEAR`

## 현재 판정

**Reference Build: 기준본 준비 완료**

**Mission 상태: ⬜ NOT STARTED 유지 / Runtime 미시작 / CLEAR 아님**

다음 Phase A 작업은 **B3-2 Reference Build**입니다.
