# B3-1 Mini Redis Reference

## 실행

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

종료: `exit`, `quit`, Ctrl+D, Ctrl+C.

## 명령

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

문자열에 공백이 있으면 큰따옴표를 사용합니다.

```text
SET greeting "hello world"
```

## 구현 구조

```text
mini_redis/
├── doubly_linked_list.py
├── hash_map.py
├── min_heap.py
├── store.py
└── cli.py
```

- DoublyLinkedList: LRU 순서
- HashMap: key → CacheEntry O(1) 평균 접근
- MinHeap: 가장 빠른 TTL 만료 후보
- CacheEntry: value, LRU node, expire_at, ttl version

## 메모리 계산

공식 기준 그대로:

```text
used_memory = Σ(UTF-8 key byte length + UTF-8 value byte length)
```

Node/버킷/포인터/Heap 등의 Python 객체 오버헤드는 공식 채점식에서 제외합니다.

## LRU

성공한 SET/GET은 LRU node를 front로 이동합니다. maxmemory 초과 시 back의 가장 오래 사용되지 않은 key부터 삭제합니다.

단일 key+value 자체가 maxmemory보다 크면 다른 key를 지우지 않고 OOM으로 거부합니다.

## TTL

EXPIRE는 Entry의 `expire_at`/`ttl_version`을 갱신하고 `(expire_at, version, key)`를 직접 구현한 MinHeap에 넣습니다.

TTL 재설정/SET overwrite 때문에 과거 heap item이 남아도 version/expire_at이 현재 Entry와 다르면 stale item으로 버립니다. SET overwrite는 기존 TTL을 초기화합니다.

## 금지 자료구조

핵심 `mini_redis` 구현에서 다음을 사용하지 않습니다.

- `dict`
- `set`
- `collections`
- `heapq`

Python list는 해시 버킷 배열과 heap 배열처럼 인덱스 기반 자료구조를 직접 구현하는 용도로 사용합니다.

## 검증

```bash
bash training/round-01-clear/environment/verify.sh
```
