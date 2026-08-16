# B3-1 R01 Environment

## Golden Path

- Python 3.8+
- 외부 패키지 없음
- REPL 실행: `python training/round-01-clear/reference/main.py`
- 핵심 저장소 구현에 `dict`, `set`, `collections` 사용 금지

## 실행

Repository 루트에서:

```bash
export PYTHONPATH="$PWD/training/round-01-clear/reference"
python3 training/round-01-clear/reference/main.py
```

## 자동 검증

```bash
bash training/round-01-clear/environment/verify.sh
```

검증 스크립트는 Python 문법, unit tests, 핵심 금지어/import를 확인합니다. 실제 REPL 조작과 설명형 Evaluation은 Phase C에서 별도로 확인합니다.
