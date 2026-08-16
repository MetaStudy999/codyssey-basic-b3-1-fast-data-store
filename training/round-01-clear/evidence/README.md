# B3-1 R01 — Evidence Guide

## 1. 자동 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

`Result: N PASS / 0 FAIL`을 실제 결과로 저장합니다.

## 2. REPL 기본 명령

실제 터미널에서 다음 흐름을 기록합니다.

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

예시 시나리오:

```text
CONFIG SET maxmemory 6
SET a 1
SET b 22
GET a
SET c 33
GET b
INFO memory
```

실제 결과에서 `GET a` 이후 b가 LRU가 되어 제거되는지 확인합니다.

## 4. OOM

```text
CONFIG SET maxmemory 3
SET long value
```

단일 entry 자체가 제한을 초과해 기존 key를 불필요하게 evict하지 않고 OOM이 나오는지 기록합니다.

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
```

추가 edge:

- EXPIRE 재설정
- `EXPIRE key 0` 즉시 삭제
- SET overwrite 후 TTL `-1`
- DEL 후 TTL `-2`

## 6. 오류 처리

```text
GET
CONFIG SET maxmemory abc
HELLO
```

Redis-style error가 표시되는지 확인합니다.

## 7. 자료구조 설명 Evidence

평가 시 실제 코드 위치를 가리킬 수 있도록 다음 파일을 기준으로 설명합니다.

- `doubly_linked_list.py`
- `hash_map.py`
- `min_heap.py`
- `store.py`

## CLEAR

unit test만으로 CLEAR하지 않습니다. 실제 REPL 명령, LRU/TTL/OOM edge case와 설명형 Evaluation까지 확인합니다.
