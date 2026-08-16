# B3-1 R01 — Evaluation Q&A Reference

실제 평가에서는 아래 문장을 외우기보다 **본인이 실행한 코드·REPL 결과·테스트를 근거로** 설명합니다.

## 1. SET/GET 평균 O(1)이 가능한 이유는?

직접 구현 HashMap이 key의 hash로 bucket index를 계산해 전체 key를 순회하지 않고 해당 bucket chain만 확인합니다. load factor가 0.75를 넘으면 bucket을 2배로 늘려 chain이 과도하게 길어지는 것을 줄입니다. 성공한 SET/GET의 LRU 갱신은 Entry가 DoublyLinkedList node를 직접 참조하므로 해당 node를 O(1)에 front로 옮길 수 있습니다.

## 2. 해시 충돌은 어떻게 처리하는가?

서로 다른 key가 같은 bucket index를 얻으면 `_BucketNode.next`로 chain을 만듭니다. `get/remove/contains`는 계산된 하나의 bucket chain에서 key를 비교합니다. Reference test는 실제로 같은 bucket index를 갖는 두 key를 찾아 각각의 값을 보존하는지 확인합니다.

## 3. 직접 만든 hash 함수는 어떻게 index를 만드는가?

`HashMap._hash()`는 key를 UTF-8 bytes로 바꾼 뒤 FNV-1a 형태의 64-bit rolling hash를 직접 계산합니다. `_index()`는 그 결과를 현재 bucket 수로 나눈 나머지를 사용합니다. Python 내장 `hash()`나 `dict`를 저장소 구현으로 대체하지 않습니다.

## 4. 왜 load factor 0.75를 초과할 때 resize하는가?

bucket 대비 entry가 지나치게 많아지면 chain 길이가 길어지고 평균 탐색 성능이 나빠질 수 있습니다. 공식 기준은 **0.75를 초과할 때**이므로 6/8 = 0.75에서는 유지하고, 7/8 > 0.75가 되는 insertion에서 capacity를 8→16으로 확장합니다. resize 후 기존 key를 새 capacity 기준 index로 다시 배치합니다.

## 5. Doubly Linked List의 필수 연산이 O(1)인 이유는?

각 Node가 `prev`와 `next`를 직접 가리키며, head/tail sentinel을 사용합니다. 이미 Node reference를 알고 있다는 전제에서 insertion/removal/move는 인접 pointer 몇 개만 바꾸므로 데이터 개수와 관계없이 O(1)입니다. `remove_node()`나 `move_to_front()`에서 list 전체를 검색하지 않습니다.

## 6. LRU가 O(1)인 핵심 구조는?

HashMap Entry에 해당 key의 DoublyLinkedList node reference를 저장합니다. 그래서 key lookup O(1) 평균 후 node를 다시 찾지 않고 바로 `move_to_front()`할 수 있습니다. 가장 오래된 key는 list tail 바로 앞 node이므로 eviction 대상도 O(1)에 찾습니다.

## 7. GET 실패/만료에서는 왜 LRU를 갱신하지 않는가?

공식 규칙은 **성공한 GET만** 최근 사용으로 간주합니다. 없는 key나 만료되어 삭제된 key는 실제 데이터 사용이 아니므로 LRU 순서를 바꾸지 않습니다.

## 8. GET 명령의 전체 흐름은?

1. 해당 key의 TTL 만료 여부를 먼저 확인합니다.
2. 만료되었다면 store/LRU/memory/TTL 논리 상태에서 삭제하고 `(nil)`로 끝냅니다.
3. 만료되지 않았다면 HashMap에서 Entry를 조회합니다.
4. key가 없으면 `(nil)`입니다.
5. 값이 존재하는 경우에만 LRU node를 front로 이동합니다.
6. value를 Redis-style 문자열로 반환합니다.

이 순서 때문에 만료된 key가 LRU 최근 사용으로 잘못 갱신되지 않습니다.

## 9. used_memory는 무엇을 포함하는가?

공식식 그대로 UTF-8 key byte 길이 + UTF-8 value byte 길이의 합만 포함합니다. Python object, Node, pointer, bucket, heap overhead는 공식 채점식에서 제외합니다.

## 10. 메모리 초과 시 eviction 흐름은?

1. SET 전에 만료된 key를 purge합니다.
2. 새 entry 하나의 key+value byte 크기를 계산합니다.
3. 그 단일 entry 자체가 maxmemory보다 크면 기존 데이터에 손대지 않고 OOM으로 거부합니다.
4. 그렇지 않으면 SET/overwrite를 적용하고 `used_memory`를 갱신합니다.
5. `maxmemory > 0`이고 used_memory가 제한을 초과하면 LRU tail부터 삭제합니다.
6. 각 eviction에서 해당 entry byte 수를 used_memory에서 빼고 `evicted_keys`를 1 증가시킵니다.
7. `used_memory <= maxmemory`가 될 때까지 반복합니다.

## 11. 단일 entry가 maxmemory보다 크면 왜 기존 key를 지우지 않는가?

그 entry 하나만으로도 제한 안에 들어갈 수 없으므로 기존 데이터를 모두 evict해도 성공할 수 없습니다. 따라서 기존 key를 보호하고 SET 자체를 OOM으로 거부합니다. Reference test는 OOM 이후 기존 key와 `evicted_keys`가 유지되는지 확인합니다.

## 12. SET overwrite에서 메모리와 TTL은 어떻게 처리하는가?

기존 key/value byte 비용을 used_memory에서 빼고 새 value 비용을 더합니다. 같은 Entry/LRU node를 재사용해 front로 이동하며, `ttl_version`을 증가시키고 `expire_at=None`으로 만들어 공식 요구인 TTL 초기화를 수행합니다.

## 13. TTL에 heap이 적합한 이유는?

가장 빨리 만료될 key의 expire_at을 빠르게 확인해야 하기 때문입니다. MinHeap의 root에서 최소 expire_at을 O(1)로 확인하고 push/pop은 O(log n)입니다. 전체 key를 매번 순회해 가장 이른 만료를 찾는 O(n) 접근을 피할 수 있습니다.

## 14. EXPIRE를 여러 번 설정하면 과거 heap item은 어떻게 처리하는가?

heap 중간 item을 직접 찾아 삭제하면 비용과 구현 복잡도가 커집니다. Entry의 `ttl_version`과 현재 `expire_at`을 함께 비교해 오래된 heap item을 stale로 판정하고 root까지 올라왔을 때 버리는 lazy deletion을 사용합니다.

## 15. DEL 때 TTL 구조도 왜 정리해야 하는가?

store에서 key만 제거하고 LRU/TTL reference를 그대로 유효하게 두면 이후 stale item이 잘못된 상태를 만들 수 있습니다. Reference는 Entry를 store와 LRU에서 제거하고 TTL version을 증가시켜 과거 heap item을 **논리적으로 무효화**합니다. heap 배열에서 즉시 중간 삭제하지 않는 것은 공식 미션이 허용한 lazy deletion 전략입니다. 같은 key를 다시 SET해도 과거 TTL version이 새 Entry와 일치하지 않아 새 데이터를 삭제하지 않습니다.

## 16. LRU 대신 LFU를 구현한다면 무엇이 달라지는가?

LRU는 최근 사용 순서를 DoublyLinkedList 하나로 관리하지만 LFU는 **사용 빈도**가 핵심입니다. 최소한 key별 frequency가 필요하고, 같은 frequency 안에서는 tie-break를 위한 최근성 순서가 필요할 수 있습니다. 일반적인 O(1) LFU 설계라면 `key → entry/frequency node` HashMap과 `frequency → key list` 구조, 그리고 현재 최소 frequency 추적값을 둡니다. 단순히 현재 LRU list만 재사용해서는 빈도 기반 제거를 정확히 구현할 수 없습니다.

## 17. 데이터가 10만 건으로 늘어나면 병목은 어디인가?

평균 GET/SET은 HashMap과 LRU 덕분에 효율적이지만 다음 부분이 커질 수 있습니다.

- `KEYS`: 전체 key를 순회하므로 O(n)
- HashMap resize: 확장 순간 전체 entry 재배치 O(n)
- TTL heap: stale item이 많이 쌓이면 heap memory와 purge 비용 증가
- Python object overhead: 공식 used_memory 식에는 없지만 실제 프로세스 메모리에서는 큼
- single-thread REPL: 많은 요청을 동시에 처리하지 못함

개선 방향은 incremental rehash, cursor 기반 SCAN, stale heap compaction/rebuild, 실제 메모리 계측, 네트워크/동시성 구조 등입니다. 다만 R01에서는 공식 자료구조 학습 범위를 먼저 충족합니다.

## 18. used_memory에 자료구조 오버헤드까지 포함하면 무엇이 달라지는가?

현재 공식식은 key/value UTF-8 bytes만 계산하므로 구현 언어와 객체 구조에 영향을 덜 받습니다. 실제 Node, bucket array, CacheEntry, heap tuple, allocator fragmentation까지 포함하면 같은 논리 데이터라도 구현 방식과 Python 버전에 따라 메모리 값이 달라집니다. 따라서 eviction 시점도 더 빨라질 수 있습니다.

## 19. 오버헤드 포함 모델을 채점에 사용한다면 어떤 보정이 필요한가?

공정한 비교를 위해 측정 기준을 먼저 고정해야 합니다. 예를 들면 Python 버전, 플랫폼, 객체 크기 측정 방식, allocator/fragmentation 포함 여부, 공통 샘플 데이터와 측정 시점 등을 동일하게 해야 합니다. 그렇지 않으면 자료구조 설계 차이가 아니라 런타임/환경 차이가 점수에 섞입니다. 그래서 현재 미션은 공식적으로 key/value UTF-8 byte 합만 사용합니다.

## 20. 단일 스레드에서도 구조적으로 문제가 될 수 있는 지점은?

한 명령 도중 여러 구조(store/LRU/heap/used_memory)를 함께 갱신하므로 중간에 예외가 나면 불일치 가능성이 있습니다. R01 Reference는 각 명령의 갱신 순서를 단순하게 유지하고 unit test로 edge case를 확인합니다. 동시성까지 요구되지는 않지만 production에서는 transaction/lock/복구 전략이 추가로 필요합니다.
