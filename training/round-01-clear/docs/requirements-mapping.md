# B3-1 R01 — Requirement / Implementation / Verification / Evidence

실제 Runtime을 하지 않은 항목은 Evidence 완료로 표시하지 않습니다.

| ID | Requirement | Reference Implementation | Verification | Runtime Evidence |
|---|---|---|---|---|
| R01 | DLL `prev/next/data` | `doubly_linked_list.py` | 필드/연결 unit test | 코드 설명 |
| R02 | DLL 6 methods, O(1) | same | 6개 연산 unit + pointer 구조 설명 | 평가 설명 |
| R03 | HashMap `put/get/remove/contains/keys/size` | `hash_map.py` | unit | 테스트/코드 |
| R04 | 직접 hash 함수 | `HashMap._hash/_index` | 코드/평가 Q&A | 코드 설명 |
| R05 | chaining collision | `_BucketNode.next` | 실제 same-bucket collision test | 테스트 결과 |
| R06 | load factor `> 0.75` → 2x | `put/_resize` | `0.75` 유지 + `>0.75` resize 경계 test | 테스트 결과 |
| R07 | MinHeap `push/pop/peek/size` | `min_heap.py` | order/size unit | 테스트 결과 |
| R08 | `_heapify_up/down` | same | multiple-order unit/code | 테스트/설명 |
| R09 | SET/GET/DEL/EXISTS/DBSIZE/KEYS | store + cli | unit/smoke | `repl-session.txt` |
| R10 | quoted value + REPL + exit/quit | `shlex.split`, `repl` | quoted/unit + quit path | 실제 REPL |
| R11 | Redis-style errors | `cli.py` | wrong args/integer/unknown/syntax/OOM tests | 실제 오류 출력 |
| R12 | `maxmemory=0` unlimited | store | large-value unit | INFO/REPL |
| R13 | official UTF-8 `used_memory` | `_entry_bytes` | UTF-8 + overwrite accounting test | INFO output |
| R14 | SET over limit → repeated LRU eviction | `set/_evict_lru` | GET-based LRU + repeated eviction test | Before/After |
| R15 | successful SET overwrite refreshes LRU | `set` | overwrite LRU test | eviction sequence |
| R16 | successful GET refreshes LRU only | `get` | GET LRU + expired/missing behavior | eviction sequence |
| R17 | single entry > max → OOM | pre-insert size check | existing-data preservation test | OOM + existing GET |
| R18 | INFO memory 3 fields | `memory_info`/CLI | CLI field test | INFO output |
| R19 | EXPIRE/TTL semantics | store + heap | `-2/-1/N`, immediate expire tests | actual time TTL |
| R20 | EXPIRE reset lazy deletion | `ttl_version` | stale heap item deterministic test | actual reset sequence |
| R21 | SET overwrite TTL reset | `set` | stale old heap + TTL reset test | TTL output |
| R22 | DEL cleans data/LRU/memory and invalidates TTL | `_delete_key` | delete + same-key reinsert stale TTL test | command sequence |
| R23 | expired key handled before key commands | `_expire_if_needed/_purge_expired` | GET/EXISTS/DEL/TTL/DBSIZE/KEYS test | actual expiry sequence |
| R24 | no `dict/set/collections/heapq` core replacement | core implementation | AST verifier | verify output |
| R25 | Python 3.8+ | environment | verifier | version output |
| R26 | GET full flow explanation | `store.get` + Q&A | code walkthrough | evaluator check |
| R27 | LRU → LFU extension reasoning | Q&A 16 | user explanation | evaluator check |
| R28 | 100k bottleneck/improvement reasoning | Q&A 17 | user explanation | evaluator check |
| R29 | overhead-inclusive memory model | Q&A 18 | user explanation | evaluator check |
| R30 | fair scoring normalization | Q&A 19 | user explanation | evaluator check |
| R31 | Reference/Runtime separation | `REFERENCE-STATUS.md`, Checklist | status review | runtime-only evidence |

## Runtime 핵심 시나리오

1. 기본 String 6개 명령
2. `CONFIG SET maxmemory 0` unlimited
3. UTF-8 memory formula + `INFO memory`
4. LRU: `SET A/B → GET A → SET C → B eviction`
5. SET overwrite도 LRU refresh되는 시나리오
6. single-entry OOM 후 기존 key 보존
7. EXPIRE → TTL → 실제 시간 경과 → GET/EXISTS/DBSIZE
8. EXPIRE 재설정
9. `EXPIRE key 0` 즉시 만료
10. SET overwrite → TTL `-1`
11. DEL 후 TTL `-2`
12. wrong args / integer / unknown / syntax / OOM error
13. Evaluation 자기 말 설명

## Runtime Evidence 파일 기준

Phase C에서 JIT로 다음을 만듭니다.

```text
evidence/runtime/
├── verify-output.txt
├── repl-session.txt
└── evaluation-self-check.md
```

`verify.sh --runtime`은 이 파일들의 존재, verify 0 FAIL, 필수 REPL command/error group, obvious Secret/credential assignment 부재를 확인합니다.
