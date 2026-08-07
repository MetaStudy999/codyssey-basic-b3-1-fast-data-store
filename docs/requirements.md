# B3-1 Requirement & Evaluation Mapping

## Source state

- Mission PDF: VALID
- Mission Markdown: PDF 파생 DUPLICATE
- Evaluation Markdown: VALID
- Source Mode: FULL SOURCE
- Source Confidence: HIGH

## Functional requirements

| ID | Requirement | Implementation | Test |
|---|---|---|---|
| R01 | SET/GET/DEL/EXISTS/DBSIZE/KEYS | `store.py`, `cli.py` | `test_store.py`, `test_cli.py` |
| R02 | CONFIG SET maxmemory / INFO memory | `store.py`, `cli.py` | memory tests |
| R03 | EXPIRE/TTL + expiration | `store.py` | fake-clock TTL tests |
| R04 | standard error output | `cli.py` | CLI error tests |
| R05 | custom DLL | `doubly_linked_list.py` | link/invariant tests |
| R06 | custom Hash Map/chaining/resize | `hash_map.py` | collision/resize tests |
| R07 | custom Min Heap | `min_heap.py` | ordering/boundary test |
| R08 | LRU update/eviction | `store.py` | LRU tests |
| R09 | overwrite/delete/expired-GET consistency | `store.py` | edge-case tests |
| R10 | no dict/set/collections replacement | `src/` | static checker |

## Evaluation mapping

평가문항 항목 1은 자동 테스트와 REPL transcript로 검증합니다. 항목 2~4의 설명형 기준은 `docs/learning.md`에서 실제 코드와 연결하여 답합니다.
