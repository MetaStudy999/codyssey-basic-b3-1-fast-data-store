# B3-1 Learning — Mini Redis를 자료구조로 설명하기

## 1. 전체 그림

```text
CLI Command
    |
    v
MiniRedis
    |
    +--> Custom HashMap ------> key -> Entry(value, LRU node)
    |
    +--> DoublyLinkedList ----> MRU <-> ... <-> LRU
    |
    +--> Custom HashMap ------> key -> active expire_at
    |
    +--> MinHeap -------------> (expire_at, key), earliest first
```

핵심은 같은 key를 여러 역할의 자료구조가 함께 추적하되, 실제 값의 Single Source는 data Hash Map이라는 점입니다.

## 2. Doubly Linked List가 O(1)인 이유

`Node`는 `prev`, `next`, `data`를 가집니다. `remove_node(node)`는 이미 node를 알고 있으므로 탐색하지 않고 앞뒤 포인터만 다시 연결합니다. `move_to_front(node)`도 같은 방식으로 기존 위치에서 분리한 뒤 head 앞에 연결합니다.

따라서 **알려진 node의 삽입/삭제/이동은 O(1)** 입니다. LRU에서는 `Entry.lru_node`가 해당 node를 직접 보관하므로 성공한 GET에서 리스트 탐색이 필요 없습니다.

## 3. Hash Map: hash function, chaining, resize

`HashMap._hash()`는 key의 UTF-8 byte를 순회하며 FNV-1a 형태로 값을 누적하고 현재 bucket capacity로 나눈 나머지를 index로 사용합니다.

서로 다른 key가 같은 index를 만들 수 있으므로 각 bucket은 Doubly Linked List입니다. 같은 bucket 안에서 `HashPair(key, value)`를 순회하여 실제 key를 비교합니다. 이것이 **collision chaining**입니다.

새 key를 넣은 뒤 `size / capacity > 0.75`가 되면 capacity를 2배로 만들고 모든 기존 pair를 새 capacity 기준으로 다시 hashing합니다.

- 평균: put/get/remove O(1)
- 최악: collision이 한 bucket에 몰리면 O(n)
- resize 한 번: O(n), 여러 삽입에 분산하면 amortized O(1)

## 4. Hash Map + DLL로 O(1) LRU를 만드는 이유

LRU에서 필요한 작업은 두 가지입니다.

1. key의 Entry를 빠르게 찾기: Hash Map 평균 O(1)
2. 사용된 key를 MRU(front)로 이동: 알려진 DLL node를 O(1)로 이동

Hash Map만 있으면 "가장 오래 사용하지 않은 key"의 순서를 유지하기 어렵고, Linked List만 있으면 key 조회 시 O(n) 탐색이 필요합니다. 둘을 조합하면 조회와 순서 갱신을 동시에 효율적으로 처리할 수 있습니다.

`SET`과 성공한 `GET`은 MRU로 이동합니다. 만료된 GET은 먼저 key를 삭제하므로 LRU를 갱신하지 않습니다.

## 5. Min Heap이 TTL에 맞는 이유

TTL 관리에서 반복적으로 필요한 질문은 **"가장 빨리 만료될 항목은 무엇인가?"** 입니다.

Min Heap은 다음 성질을 가집니다.

- earliest expiry 확인 `peek`: O(1)
- expiry 추가 `push`: O(log n)
- earliest expiry 제거 `pop`: O(log n)

이 구현은 `(expire_at, key)`를 heap에 넣습니다. 같은 key에 EXPIRE를 다시 설정하거나 SET/DEL로 TTL이 없어지면 옛 heap record를 즉시 임의 삭제하지 않고, custom Hash Map의 active TTL을 최신값으로 유지합니다. heap top에 도달한 과거 record가 active TTL과 다르면 버립니다. 이것이 **lazy deletion**입니다.

## 6. GET 전체 흐름

```text
GET key
  -> active TTL 조회
  -> expire_at <= now ?
       YES: data/LRU/active TTL 삭제 -> (nil)
       NO : data HashMap 조회
  -> key 없음 ? (nil)
  -> key 있음: LRU node를 front로 이동
  -> "value" 반환
```

만료된 GET은 LRU touch를 하지 않는다는 평가 조건이 이 순서에서 자연스럽게 보장됩니다.

## 7. memory accounting과 eviction

공식 계산식은 다음뿐입니다.

```text
used_memory = Σ(len(utf8(key)) + len(utf8(value)))
```

노드/포인터/bucket overhead는 계산하지 않습니다.

SET 흐름:

1. 새 단일 entry의 byte 크기가 maxmemory 자체보다 크면 OOM, 저장하지 않음
2. insert/update 후 used_memory 갱신
3. maxmemory가 0이 아니고 초과하면 expired key를 먼저 정리
4. DLL tail(LRU)을 제거
5. 제거한 entry의 byte만큼 used_memory 감소
6. `evicted_keys += 1`
7. limit 이하가 될 때까지 반복

## 8. DEL과 TTL의 일관성

DEL은 data Hash Map과 LRU node를 즉시 제거하고 active TTL Hash Map에서도 key를 제거합니다. Min Heap에는 과거 tuple이 물리적으로 남을 수 있지만 active TTL이 없으므로 무효 record이며 이후 purge에서 버려집니다. 따라서 논리적 TTL state는 즉시 삭제됩니다.

## 9. LFU로 바꾼다면

LRU의 "최근 사용 순서 DLL" 대신 **사용 횟수(frequency)** 를 관리해야 합니다. 단순히 한 개의 DLL로는 부족합니다.

한 가지 설계는:

- key -> Entry(value, frequency, node) Hash Map
- frequency -> 해당 frequency key들의 DLL
- 현재 최소 frequency를 별도 추적

조회할 때 frequency bucket에서 node를 O(1) 제거하고 다음 frequency bucket으로 이동합니다. eviction은 최소 frequency bucket의 LRU key를 선택할 수 있습니다. 단, `frequency -> list` 인덱스도 이 미션의 금지 제약을 지키려면 custom Hash Map으로 구현해야 합니다.

## 10. 데이터가 10만 건이면 병목은?

가능한 병목:

- collision이 나쁜 hash distribution으로 한 bucket에 집중되면 chain 탐색 증가
- 많은 TTL overwrite가 발생하면 lazy stale heap record가 누적되어 heap 크기가 active TTL 수보다 커질 수 있음
- Python object/Node overhead는 공식 used_memory에는 없지만 실제 RAM에는 존재
- KEYS는 전체 key를 반환하므로 O(n)이며 큰 데이터에서는 비용이 큼

개선 방향:

- hash quality와 capacity sizing 점검
- stale heap 비율이 임계값을 넘을 때 heap rebuild를 선택적으로 수행
- incremental rehash 같은 resize latency 완화 전략
- production Redis처럼 KEYS 대신 cursor scan 계열을 고려(현재 Mission Non-scope)

## 11. 자료구조 overhead를 used_memory에 포함하면?

현재 공식 채점식은 key/value UTF-8 bytes만 계산하므로 구현 언어의 object 크기 차이를 배제합니다. overhead까지 포함하면 다음이 달라집니다.

- bucket 배열 크기
- HashPair/Entry/Node object
- prev/next reference
- heap tuple/list capacity

등이 모두 memory budget을 소비합니다. 같은 논리 데이터라도 Python 구현과 다른 언어 구현의 측정값이 크게 달라질 수 있습니다.

## 12. overhead 포함 모델의 공정한 채점 보정

공정한 비교를 위해서는 **측정 모델을 먼저 고정**해야 합니다.

예:

- 언어별 실제 object size를 그대로 비교하지 않고, 추상적인 고정 cost table을 정의
- `entry = key bytes + value bytes + fixed_entry_overhead`처럼 동일 공식 적용
- bucket/node/heap record의 단위 cost를 명시
- capacity의 unused slot까지 포함할지 규칙 고정
- 같은 dataset과 같은 command sequence로 비교

이 미션에서는 공식 Source가 overhead 제외를 명시하므로 위 모델은 확장 사고일 뿐 구현에 적용하지 않습니다.

## 13. 자기 설명 체크

다음 질문을 코드 파일을 열고 직접 설명할 수 있으면 평가 준비가 됩니다.

- 왜 DLL node를 Entry가 직접 들고 있어야 LRU 이동이 O(1)인가?
- Hash collision이 발생한 두 key가 어떻게 같은 bucket에서 구분되는가?
- 왜 resize 때 기존 key를 다시 hash해야 하는가?
- TTL heap의 stale record가 왜 삭제된 key를 다시 지우지 못하는가?
- SET overwrite가 TTL을 왜/어디서 초기화하는가?
- `used_memory`가 어떤 순간에 증가/감소하는가?
