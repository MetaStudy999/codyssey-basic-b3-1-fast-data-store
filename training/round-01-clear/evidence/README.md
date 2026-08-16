# B3-1 R01 — Evidence Guide

Reference Build에서는 실제 실행 결과를 만들었다고 주장하지 않습니다. Phase C에서 실제 Linux/Python Runtime으로 아래 Evidence를 JIT 생성합니다.

## Runtime Evidence 구조

```text
evidence/runtime/
├── verify-output.txt
├── repl-session.txt
└── evaluation-self-check.md
```

실제 실행 전에는 위 runtime 파일을 만들 필요가 없습니다.

## 1. 자동 검증

Repository 루트에서:

```bash
bash training/round-01-clear/environment/verify.sh | tee training/round-01-clear/evidence/runtime/verify-output.txt
```

정상 기준:

```text
Result: N PASS / 0 FAIL
```

실제로 실행한 결과만 저장합니다.

## 2. REPL 기본 명령

실제 터미널에서 다음 흐름을 `repl-session.txt`에 기록합니다.

```text
SET name Alice
GET name
EXISTS name
DBSIZE
KEYS
DEL name
GET name
```

## 3. maxmemory / LRU

공식 UTF-8 byte 식을 계산할 수 있는 작은 key/value를 사용합니다.

대표 시나리오:

```text
CONFIG SET maxmemory 6
SET a 1
SET b 22
GET a
SET c 33
GET b
INFO memory
```

실제 결과에서 `GET a` 이후 `b`가 LRU가 되어 제거되는지 확인합니다.

SET overwrite도 성공한 SET이므로 LRU를 갱신하는지 별도로 확인합니다.

## 4. OOM

기존 데이터가 있는 상태에서 단일 entry 자체가 maxmemory보다 큰 경우를 확인합니다.

```text
CONFIG SET maxmemory 3
SET a 1
SET long value
GET a
INFO memory
```

확인점:

- 새 entry는 OOM
- 기존 `a`는 유지
- 실패한 oversized entry 때문에 `evicted_keys`가 증가하지 않음

## 5. TTL

```text
CONFIG SET maxmemory 0
SET temp value
TTL temp
EXPIRE temp 2
TTL temp
# 실제 2초 이상 경과
GET temp
TTL temp
DBSIZE
```

추가 edge:

- EXPIRE 재설정 후 과거 만료 시점이 새 TTL을 삭제하지 않음
- `EXPIRE key 0` 즉시 삭제
- SET overwrite 후 TTL `-1`
- DEL 후 TTL `-2`

Runtime Evidence에서는 unit-test의 가짜 clock이 아니라 **실제 시간 경과**도 한 번 확인합니다.

## 6. 오류 처리

```text
GET
CONFIG SET maxmemory abc
HELLO
SET broken "quote
```

Redis-style error가 표시되는지 확인합니다.

## 7. 자료구조 설명 Evidence

`evaluation-self-check.md`에는 실제 코드 위치를 근거로 다음을 자기 말로 정리합니다.

- Doubly Linked List 6개 연산과 O(1)
- 직접 hash 함수
- chaining collision
- load factor 0.75 / resize
- HashMap + Linked List O(1) LRU
- MinHeap TTL
- GET 전체 처리 흐름
- memory eviction 흐름
- LRU → LFU 변경 아이디어
- 10만 건 병목
- 자료구조 overhead 포함 memory model
- 공정한 비교/채점 보정 기준

## 8. Secret / 개인정보

B3-1 공식 미션에는 Secret이 필요하지 않습니다. Evidence에 다음을 넣지 않습니다.

- Password
- API Key
- Access Token
- Private Key
- 개인 인증정보

## Final Runtime Gate

Evidence를 만든 뒤:

```bash
bash training/round-01-clear/environment/verify.sh --runtime
```

`0 FAIL`이어야 하며, unit test만으로 B3-1을 CLEAR 처리하지 않습니다. 실제 REPL, LRU/OOM/TTL edge, 실제 시간 경과, Evaluation 설명까지 확인한 뒤에만 `✅ CLEAR`가 가능합니다.
