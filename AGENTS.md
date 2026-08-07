# AGENTS.md — B3-1 Mini Redis

## ROLE

이 저장소의 작업자는 B3-1 Mission의 구현자 또는 검증자다.

## SOURCE OF TRUTH

1. `b3-1-mission.pdf`
2. `b3-1-mission.md`
3. `b3-1-evaluation.md`
4. `MISSION-WORK-PACKET.md`
5. README / learning docs / code / tests / evidence

일반적인 Redis 구현 관행은 공식 Source를 변경하지 않는다.

## WORKSPACE BOUNDARY

- WRITE: `MetaStudy999/codyssey-basic-b3-1-fast-data-store`만
- DO NOT WRITE: Control Tower `MetaStudy999/codyssey-basic` 또는 다른 Mission repo
- Work branch: `mission/b3-1`

## REQUIRED FOCUS

- custom hash map + chaining + resize
- doubly linked list and O(1) node moves
- min heap ordering
- LRU updates and eviction
- TTL/expiration and stale heap handling
- official memory accounting
- REPL commands and standard errors
- edge cases: overwrite TTL reset, expired GET, delete consistency, OOM

## PROHIBITIONS

- `dict`, `set`, `collections`로 Hash Map/Cache를 대체하지 않는다.
- Source가 요구하지 않는 네트워크, 영속성, 동시성, 복잡 Redis 자료형을 추가하지 않는다.
- 실제 실행하지 않은 테스트나 출력은 PASS/Evidence로 기록하지 않는다.
- secret/credential을 추가하거나 commit하지 않는다.
- 현재 Mission PASS와 무관한 대규모 리팩터링을 하지 않는다.

## BEGINNER LEARNING PRESERVATION

코드는 자료구조의 역할과 연결을 학습자가 설명할 수 있을 정도로 단순하고 명시적으로 유지한다. 핵심 자료구조는 독립 모듈로 두고 핵심 메서드에 docstring을 작성한다.

## TEST COMMANDS

```bash
python -m compileall -q src main.py tests
python -m unittest discover -s tests -v
```

추가 정적 확인:

```bash
python scripts/check_forbidden_builtins.py
```

## REVIEW CONTRACT

첫 검토에서는 코드를 수정하지 말고 아래만 보고한다.

- BLOCKER
- MAJOR
- 필수 요구 누락
- 실패 테스트
- 허위 PASS/Evidence
- secret 노출

MINOR/IMPROVEMENT는 현재 미션 완료를 막지 않는다.

## STATUS

- TODO: 미구현/미실행
- IMPLEMENTED: 구현됨, 검증 전
- TESTED: 자동 테스트 완료
- PASS: 필수 구현 + 실제 검증 + Evidence 완료
- NEEDS-RUNTIME: 현재 하네스 밖 실제 실행 필요
- BLOCKED: 외부 조건으로 진행 불가

## STOP CONDITION

공식 필수 요구와 Evaluation이 충족되고, 필수 테스트/Evidence가 완료되며, BLOCKER=0, MAJOR=0이면 검토와 구현을 종료한다.
