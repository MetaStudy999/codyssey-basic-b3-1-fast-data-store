import json
import shlex
from typing import List

from .store import MiniRedis, OOMError

ERR_INTEGER = "(error) ERR value is not an integer or out of range"
ERR_OOM = "(error) OOM command not allowed when used_memory > 'maxmemory'"


def _wrong_args(command: str) -> str:
    return "(error) ERR wrong number of arguments for '{}' command".format(command.upper())


def _integer(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(ERR_INTEGER) from exc


def _render_keys(keys: List[str]) -> str:
    if not keys:
        return "(empty array)"
    lines: List[str] = []
    for index, key in enumerate(keys, start=1):
        lines.append("{}) {}".format(index, json.dumps(key, ensure_ascii=False)))
    return "\n".join(lines)


def execute(store: MiniRedis, line: str) -> str:
    try:
        parts = shlex.split(line)
    except ValueError:
        return "(error) ERR syntax error"

    if not parts:
        return ""

    command = parts[0].upper()

    try:
        if command == "SET":
            if len(parts) != 3:
                return _wrong_args(command)
            try:
                store.set(parts[1], parts[2])
            except OOMError:
                return ERR_OOM
            return "OK"

        if command == "GET":
            if len(parts) != 2:
                return _wrong_args(command)
            value = store.get(parts[1])
            return "(nil)" if value is None else json.dumps(value, ensure_ascii=False)

        if command == "DEL":
            if len(parts) != 2:
                return _wrong_args(command)
            return "(integer) {}".format(store.delete(parts[1]))

        if command == "EXISTS":
            if len(parts) != 2:
                return _wrong_args(command)
            return "(integer) {}".format(store.exists(parts[1]))

        if command == "DBSIZE":
            if len(parts) != 1:
                return _wrong_args(command)
            return "(integer) {}".format(store.dbsize())

        if command == "KEYS":
            if len(parts) != 1:
                return _wrong_args(command)
            return _render_keys(store.keys())

        if command == "CONFIG":
            if len(parts) != 4:
                return _wrong_args(command)
            if parts[1].upper() != "SET" or parts[2].lower() != "maxmemory":
                return "(error) ERR syntax error"
            value = _integer(parts[3])
            if value < 0:
                return ERR_INTEGER
            store.configure_maxmemory(value)
            return "OK"

        if command == "INFO":
            if len(parts) != 2:
                return _wrong_args(command)
            if parts[1].lower() != "memory":
                return "(error) ERR syntax error"
            used, maximum, evicted = store.memory_info()
            return "used_memory:{} maxmemory:{} evicted_keys:{}".format(used, maximum, evicted)

        if command == "EXPIRE":
            if len(parts) != 3:
                return _wrong_args(command)
            seconds = _integer(parts[2])
            return "(integer) {}".format(store.expire(parts[1], seconds))

        if command == "TTL":
            if len(parts) != 2:
                return _wrong_args(command)
            return "(integer) {}".format(store.ttl(parts[1]))

        return "(error) ERR unknown command '{}'".format(parts[0])

    except ValueError as exc:
        if str(exc) == ERR_INTEGER:
            return ERR_INTEGER
        return "(error) ERR {}".format(exc)


def repl() -> None:
    store = MiniRedis()
    while True:
        try:
            line = input("mini-redis> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if line.strip().lower() in ("exit", "quit"):
            return
        result = execute(store, line)
        if result:
            print(result)
