# B3-1 R01 — Evaluation Q&A Reference

## 1. SET/GET 평균 O(1)이 가능한 이유는?

직접 구현 HashMap이 key의 hash로 bucket index를 계산해 전체 key를 순회하지 않고 해당 bucket chain만 확인합니다. load factor가 0.75를 넘으면 bucket을 2배로 늘려 chain이 과도하게 길어지는 것을 줄입니다. 성공한 SET/GET의 LRU 갱신은 Entry가 DoublyLinkedList node를 직접 참조하므로 해당 node를 O(1)에 front로 옮길 수 있습니다.

## 2. 해시 충돌은 어떻게 처리하는가?

서로 다른 key가 같은 bucket index를 얻으면 `_BucketNode`의 `next`로 chain을 만듭니다. get/remove는 그 bucket chain에서 key를 비교합니다.

## 3. 왜 load factor 0.75에서 resize하는가?

bucket 대비 entry가 지나치게 많아지면 chain 길이가 길어지고 평균 탐색 성능이 나빠질 수 있습니다. 0.75는 공간과 충돌 가능성 사이의 균형을 잡는 학습 기준입니다.

## 4. LRU가 O(1)인 핵심 구조는?

HashMap Entry에 해당 key의 DoublyLinkedList node reference를 저장합니다. 그래서 key lookup O(1) 평균 후 node를 다시 찾지 않고 바로 `move_to_front()`할 수 있습니다. 가장 오래된 key는 list tail 바로 앞 node입니다.

## 5. GET 실패/만료에서는 왜 LRU를 갱신하지 않는가?

공식 규칙은 **성공한 GET만** 최근 사용으로 간주합니다. 없는 key나 만료되어 삭제된 key는 실제 데이터 사용이 아니므로 LRU 순서를 바꾸지 않습니다.

## 6. used_memory는 무엇을 포함하는가?

공식식 그대로 UTF-8 key byte 길이 + UTF-8 value byte 길이의 합만 포함합니다. Python object, Node, pointer, bucket, heap overhead는 공식 채점식에서 제외합니다.

## 7. 단일 entry가 maxmemory보다 크면 왜 기존 key를 지우지 않는가?

그 entry 하나만으로도 제한 안에 들어갈 수 없으므로 기존 데이터를 모두 evict해도 성공할 수 없습니다. 따라서 기존 key를 보호하고 SET 자체를 OOM으로 거부합니다.

## 8. SET overwrite에서 메모리와 TTL은 어떻게 처리하는가?

기존 key/value byte 비용을 used_memory에서 빼고 새 value 비용을 더합니다. 같은 Entry/LRU node를 재사용해 front로 이동하며, `ttl_version`을 증가시키고 `expire_at=None`으로 만들어 공식 요구인 TTL 초기화를 수행합니다.

## 9. TTL에 heap이 적합한 이유는?

가장 빨리 만료될 key의 expire_at이 항상 필요하기 때문입니다. MinHeap의 root에서 최소 expire_at을 O(1)로 확인하고 push/pop은 O(log n)입니다. 전체 key를 매번 스캔할 필요가 없습니다.

## 10. EXPIRE를 여러 번 설정하면 과거 heap item은 어떻게 처리하는가?

heap 중간 item을 직접 찾아 삭제하면 비용과 구현 복잡도가 커집니다. Entry의 `ttl_version`과 현재 `expire_at`을 함께 비교해 오래된 heap item을 stale로 판정하고 root까지 올라왔을 때 버리는 lazy deletion을 사용합니다.

## 11. DEL 때 TTL 구조도 왜 정리해야 하는가?

store에서 key만 제거하고 LRU/TTL reference를 남기면 이후 stale entry가 잘못된 상태를 만들 수 있습니다. Reference는 DEL에서 Entry를 제거하고 LRU node를 떼며 TTL version을 증가시켜 기존 heap item을 무효화합니다.

## 12. 단일 스레드에서도 구조적으로 문제가 될 수 있는 지점은?

한 명령 도중 여러 구조(store/LRU/heap/used_memory)를 함께 갱신하므로 중간에 예외가 나면 불일치 가능성이 있습니다. R01 Reference는 각 명령의 갱신 순서를 단순하게 유지하고 unit test로 edge case를 확인합니다. 동시성까지 요구되지는 않지만 production에서는 transaction/lock/복구 전략이 추가로 필요합니다.

## 13. 실제 Redis라면 used_memory를 어떻게 개선해야 하는가?

실제 시스템은 allocator metadata, object/header, hash table bucket, linked node, fragmentation 등을 포함한 실제 메모리 사용을 측정해야 합니다. B3-1은 공식 학습식에 따라 key/value UTF-8 bytes만 계산합니다.

## 14. O(1) LRU 대신 간단한 방법을 쓰면 어떤 문제가 있는가?

접근할 때마다 list 전체에서 key를 찾으면 O(n)이 됩니다. 데이터가 많아질수록 GET/SET latency가 커집니다. HashMap에서 LRU node를 직접 가리키는 방식이 이 탐색을 제거합니다.
