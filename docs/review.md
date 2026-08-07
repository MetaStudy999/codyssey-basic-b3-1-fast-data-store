# B3-1 G4 Review

## Verdict

`PASS-CANDIDATE`

- BLOCKER: **0**
- MAJOR: **0**
- Secret/Credential exposure: **0**
- Required-function gap: **0**

## Review basis

한 차례의 self review에서 다음 순서로 대조했다.

1. `b3-1-mission.pdf`
2. `b3-1-mission.md`
3. `b3-1-evaluation.md`
4. `MISSION-WORK-PACKET.md`
5. `src/mini_redis/*`
6. `tests/*`
7. 실제 실행 Evidence

판정 우선순위는 `Source → reproducible test → runtime → evidence`를 사용했다.

## Requirement-focused review

### Custom data structures

- Hash Map은 직접 hash function을 사용한다.
- collision은 bucket별 Doubly Linked List chaining으로 처리한다.
- load factor가 0.75를 초과하면 capacity를 2배로 확장하고 rehash한다.
- LRU list는 Entry가 자신의 node를 직접 보관하여 알려진 node의 이동/삭제가 O(1)이다.
- Min Heap은 explicit `_heapify_up` / `_heapify_down`으로 TTL tuple을 정렬한다.
- `dict`, `set`, `collections`로 핵심 저장 구조를 우회하지 않는다.

### LRU / memory

- 성공한 SET/GET만 MRU(front)를 갱신한다.
- 만료된 GET은 먼저 삭제되고 LRU 갱신을 하지 않는다.
- 공식 UTF-8 key/value byte 공식만 `used_memory`에 반영한다.
- maxmemory 초과 후 LRU tail부터 eviction하며 `evicted_keys`를 누적한다.
- 단일 entry 자체가 maxmemory보다 크면 기존 값을 훼손하지 않고 OOM을 반환한다.

### TTL

- active TTL은 custom Hash Map으로 관리한다.
- Min Heap의 stale tuple은 lazy deletion으로 무효화한다.
- overwrite SET은 active TTL을 제거한다.
- DEL은 data/LRU/active TTL을 즉시 제거한다.
- `DBSIZE`/`KEYS`도 heap purge를 통해 이미 만료된 key를 제외한다.

### REPL / errors

- `mini-redis>` REPL과 `exit`/`quit`을 제공한다.
- quoted value를 `shlex`로 처리한다.
- unknown command / wrong args / integer error / OOM 출력 계약을 테스트한다.

## Review findings and disposition

| Finding | Severity | Disposition |
|---|---|---|
| 최초 test set은 `DBSIZE`/`KEYS`가 GET 없이도 만료 key를 purge하는 경로를 직접 검증하지 않았다. | TEST GAP | 테스트 추가 후 PASS |
| 최초 forbidden-builtins checker는 `dict()`/`set()` call과 imports는 잡았지만 literal/comprehension까지 검사하지 않았다. | TEST GAP | AST checker 강화 후 PASS |
| lazy TTL heap은 overwrite가 매우 많은 10만 건 수준에서 stale record가 누적될 수 있다. | BACKLOG | 현재 Mission 필수 범위 아님; `docs/learning.md` 확장 사고로 기록 |

## Actual verification

```text
python -m compileall -q src main.py tests       PASS
python -m unittest discover -s tests -v         21/21 PASS
python scripts/check_forbidden_builtins.py       PASS
interactive REPL scenario                        PASS
```

실제 출력은 다음에 저장했다.

- `evidence/test-results.txt`
- `evidence/repl-transcript.txt`

## Independent-review note

현재 ChatGPT Workcell 하네스에는 별도의 Codex/Copilot reviewer 실행 인터페이스가 제공되지 않아 외부 독립 Agent review를 수행했다고 주장하지 않는다. Workcell 규칙의 Review Budget을 넘겨 추가적인 가상 review를 만들지 않았으며, 공식 Source 대조 + 자동 테스트 + 실제 REPL 실행 + 1회 self review로 G4의 BLOCKER/MAJOR 판정을 수행했다.

## Final G4 status

- BLOCKER = 0
- MAJOR = 0
- G4 REVIEW = `PASS`
