# B3-1 R01 — Reference Status

## 판정

**Reference Build: CORE READY**

**Runtime Mission 상태: ⬜ NOT STARTED**

Reference 코드·테스트·검증 계획이 준비되었다는 의미이며, 실제 REPL/Evidence를 수행했다는 의미가 아닙니다.

## 공식 Source 기준

- `b3-1-mission.pdf`
- `b3-1-mission.md`
- `b3-1-evaluation.md`

## 자체감사에서 확인한 핵심

### 1. 자료구조 직접 구현

- Doubly Linked List: `prev`, `next`, `data`, 필수 6개 연산
- HashMap: 직접 hash, chaining, `put/get/remove/contains/keys/size`
- load factor가 0.75를 **초과**할 때 2배 resize
- MinHeap: `push/pop/peek/size`, `_heapify_up/down`
- 핵심 구현에 `dict`, `set`, `collections`, `heapq`를 사용하지 않음

### 2. Mini Redis 기능

- SET / GET / DEL / EXISTS / DBSIZE / KEYS
- CONFIG SET maxmemory / INFO memory
- EXPIRE / TTL
- quoted value REPL parsing
- Redis-style error contract

### 3. LRU / Memory

- HashMap Entry가 LRU node를 직접 참조
- 성공한 GET과 SET/overwrite에서 move-to-front
- 공식 UTF-8 key+value byte 식 사용
- 제한 초과 시 LRU부터 반복 eviction
- 단일 entry 자체가 maxmemory 초과 시 기존 데이터 보존 + OOM

### 4. TTL

- MinHeap 기반 earliest-expiration 후보 관리
- `(expire_at, ttl_version, key)` lazy deletion
- EXPIRE 재설정의 stale heap item 무효화
- DEL 후 같은 key 재삽입 시 과거 TTL이 새 key를 지우지 않음
- SET overwrite 시 TTL 초기화
- expired key는 GET/EXISTS/DEL/TTL/DBSIZE/KEYS에서 없는 key처럼 처리

## 자체감사에서 보강한 항목

- Doubly Linked List 필수 6개 연산 테스트
- 실제 chaining collision 테스트
- load factor `== 0.75`와 `> 0.75` 경계 테스트
- MinHeap size/peek/push/pop 정렬 테스트
- `maxmemory=0` unlimited
- UTF-8 overwrite memory accounting
- GET 및 SET overwrite LRU refresh
- single-entry OOM 시 기존 데이터/evicted_keys 보존
- 반복 eviction으로 `used_memory <= maxmemory` 확인
- EXPIRE 재설정/DEL/overwrite stale TTL 안전성
- expired key의 모든 주요 명령 의미
- CLI quoted value, integer/syntax/unknown/wrong-args 오류
- verifier에 `heapq` 금지 검사 추가
- `compileall` 대신 AST syntax parse로 검증 부작용 최소화
- Runtime Evidence 전용 `--runtime` gate 추가

## 아직 실제로 PASS 처리하지 않는 항목

- Python Runtime에서 `verify.sh` 실제 실행
- 실제 REPL 상호작용
- 실제 시간 경과 TTL 확인
- 실제 LRU/OOM/INFO 출력
- Runtime Evidence 파일
- 사용자의 Evaluation 자기 말 설명

## CORE READY Gate

- [x] 공식 Mission/Evaluation 요구 매핑
- [x] 최소 충분 Reference 구현
- [x] 자료구조 제약 검사
- [x] 핵심 edge-case 테스트 설계
- [x] Reference/Runtime 분리
- [x] Runtime Evidence 계획
- [x] 허위 Runtime PASS 없음
- [x] BLOCKER/MAJOR 설계 결함 없음

따라서 Phase A 기준으로 **CORE READY**로 판정합니다. 실제 `✅ CLEAR`는 Phase C Runtime 후에만 가능합니다.
