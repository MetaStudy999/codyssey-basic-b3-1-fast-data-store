# B3-1 Mini Redis

코디세이 AI/SW 기초 B3-1 **“정보를 엄청 빠르게 찾아주는 작은 저장소 만들기”** 구현입니다.

Python 내장 `dict`, `set`, `collections`로 핵심 저장소를 대체하지 않고 다음 자료구조를 직접 구현합니다.

- Hash Map: 직접 hash function + chaining + load factor 0.75 resize
- Doubly Linked List: LRU 순서와 bucket chaining에 사용
- Min Heap: TTL 만료 시각의 최소값을 빠르게 확인

## 실행

Python 3.8 이상이 필요합니다. 외부 패키지는 없습니다.

```bash
python main.py
```

프롬프트:

```text
mini-redis>
```

종료:

```text
exit
quit
```

## 필수 명령

| 범주 | 명령 |
|---|---|
| String | `SET`, `GET`, `DEL`, `EXISTS`, `DBSIZE`, `KEYS` |
| Memory | `CONFIG SET maxmemory`, `INFO memory` |
| TTL | `EXPIRE`, `TTL` |

예:

```text
mini-redis> SET user:1 "Alice"
OK
mini-redis> GET user:1
"Alice"
mini-redis> EXPIRE user:1 3
(integer) 1
mini-redis> TTL user:1
(integer) 2
```

## 구조

```text
src/mini_redis/
├── doubly_linked_list.py  # prev/next/data, O(1) node operation
├── hash_map.py            # custom hash, chaining, resize
├── min_heap.py            # TTL heap
├── store.py               # data + LRU + TTL + memory policy
└── cli.py                 # parser + REPL
```

### 핵심 흐름

`GET key`는 다음 순서로 동작합니다.

1. key의 TTL을 확인합니다.
2. 만료되었으면 data/LRU/active TTL에서 제거하고 `(nil)`을 반환합니다.
3. 살아 있으면 custom Hash Map에서 값을 찾습니다.
4. 성공한 조회만 LRU node를 맨 앞으로 이동합니다.
5. 값을 `"value"` 형식으로 반환합니다.

TTL heap은 lazy deletion을 사용합니다. `DEL`이나 TTL overwrite 시 active TTL map에서 즉시 제거하고, 과거 heap record는 heap top에 도달했을 때 무효 record로 버립니다. 따라서 삭제된 key의 TTL은 논리적으로 즉시 제거되며 stale heap record가 데이터를 다시 만료시키지 않습니다.

## 메모리 규칙

공식 산정식만 사용합니다.

```text
used_memory = Σ(len(utf8(key)) + len(utf8(value)))
```

노드/포인터/bucket 오버헤드는 포함하지 않습니다.

- `maxmemory = 0`: 무제한
- `SET` 후 초과: LRU key부터 제거
- 단일 key+value 자체가 maxmemory보다 크면 저장하지 않고 OOM
- eviction이 실제 발생할 때만 `evicted_keys` 증가

## 테스트

```bash
python -m compileall -q src main.py tests
python -m unittest discover -s tests -v
python scripts/check_forbidden_builtins.py
```

테스트는 collision chaining, resize, heap ordering, LRU, TTL, overwrite, delete consistency, OOM, quoted value, 표준 오류를 포함합니다.

실제 실행 기록은 `evidence/`에 있습니다.

## Source / 학습 / 검증

- Mission: [`b3-1-mission.pdf`](./b3-1-mission.pdf), [`b3-1-mission.md`](./b3-1-mission.md)
- Evaluation: [`b3-1-evaluation.md`](./b3-1-evaluation.md)
- 실행 계약: [`MISSION-WORK-PACKET.md`](./MISSION-WORK-PACKET.md)
- 요구사항 추적: [`docs/requirements.md`](./docs/requirements.md)
- 테스트: [`docs/testing.md`](./docs/testing.md)
- 학습 설명: [`docs/learning.md`](./docs/learning.md)

## Non-scope

Mission의 선택/비요구 범위인 네트워크 통신, 파일 영속성, Redis 복잡 자료형, 멀티스레딩/락, Pub/Sub은 구현하지 않습니다.
