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
- `dict`, `set`, `collections` 사용 금지
- Python `list`는 버킷 배열/힙 배열 등 인덱스 기반 저장소로만 사용
- 해시맵: 직접 해시 함수 + chaining + load factor 0.75 + 2배 resize
- LRU: HashMap의 Entry가 DoublyLinkedList node를 직접 참조해 성공 GET/SET에서 O(1) move-to-front
- TTL: 직접 구현 MinHeap + Entry의 `expire_at`/`ttl_version`을 이용한 lazy deletion
- `used_memory`: 공식 UTF-8 key bytes + value bytes만 합산
- 단일 엔트리 자체가 maxmemory 초과 시 저장하지 않고 OOM
- 기존 SET overwrite 시 TTL 초기화
- 모든 key 기반 조회 전 만료 확인
- CLI parsing: `shlex.split()`으로 공백 없는 값과 큰따옴표 값을 지원

## Reference Complete Path

1. 자료구조 3종 구현/테스트
2. MiniRedis store
3. String 6 commands
4. maxmemory/INFO
5. LRU eviction
6. EXPIRE/TTL
7. TTL/LRU edge cases
8. error standard
9. REPL
10. Evaluation Q&A
11. Runtime Evidence
12. CLEAR

## 상태

**Reference Build 진행 중 / Mission 상태 ⬜ NOT STARTED / Runtime 미시작**
