# B3-1 R01 — Requirement / Implementation / Verification / Evidence

| ID | Requirement | Reference Implementation | Verification | Evidence |
|---|---|---|---|---|
| R01 | DLL prev/next/data | `doubly_linked_list.py` | unit test | code/test |
| R02 | DLL 6 methods O(1) | same | unit + explanation | test/Q&A |
| R03 | HashMap put/get/remove/contains/keys/size | `hash_map.py` | unit | test |
| R04 | custom hash + chaining | `_hash`, `_BucketNode` | unit/code review | code/Q&A |
| R05 | load factor >0.75 → 2x | `put`/`_resize` | resize unit | test |
| R06 | MinHeap push/pop/peek/size | `min_heap.py` | unit | test |
| R07 | `_heapify_up/down` | same | unit/code | test |
| R08 | SET/GET/DEL/EXISTS/DBSIZE/KEYS | store+cli | unit/smoke/REPL | command log |
| R09 | Redis style output/errors | `cli.py` | CLI tests | command log |
| R10 | maxmemory 0 unlimited | store | runtime/unit | INFO output |
| R11 | official used_memory formula | `_entry_bytes` | UTF-8 test | INFO output |
| R12 | SET over max → LRU eviction | `set`, `_evict_lru` | unit/REPL | before/after |
| R13 | single entry > max → OOM | store+cli | unit | OOM output |
| R14 | successful SET/GET LRU refresh | DLL node reference | unit | eviction behavior |
| R15 | overwrite TTL reset | `set` | unit | TTL output |
| R16 | INFO used/max/evicted | `memory_info`/CLI | unit/REPL | output |
| R17 | EXPIRE/TTL semantics | store+heap | unit/REPL | TTL output |
| R18 | expired key deleted before key command | `_expire_if_needed`/purge | unit/REPL | command sequence |
| R19 | DEL cleans LRU/TTL/memory | `_delete_key` | unit | state/output |
| R20 | no dict/set/collections | core implementation | AST verify | verify output |
| R21 | REPL + exit/quit | `main.py`, `cli.repl` | actual interaction | terminal Evidence |
| R22 | evaluation explanation | `evaluation-qa.md` | user explanation | evaluator check |

## Runtime 핵심 시나리오

1. 기본 String 명령
2. maxmemory 0 unlimited
3. UTF-8 memory formula
4. LRU: SET A/B → GET A → SET C → B eviction
5. OOM single entry
6. EXPIRE → TTL → 만료 후 GET/EXISTS/DBSIZE
7. EXPIRE 재설정
8. SET overwrite → TTL -1
9. 잘못된 인자/정수/unknown command
