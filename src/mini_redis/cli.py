"""Command parser and interactive REPL for Mini Redis."""

import shlex
from typing import Tuple

from .store import MiniRedis


class CommandProcessor:
    """Parse one Redis-style command and delegate behavior to MiniRedis."""

    def __init__(self, store: MiniRedis) -> None:
        self.store = store

    @staticmethod
    def _wrong_args(command: str) -> str:
        return "(error) ERR wrong number of arguments for '" + command + "' command"

    @staticmethod
    def _integer_error() -> str:
        return "(error) ERR value is not an integer or out of range"

    @staticmethod
    def _parse_nonnegative_int(raw: str) -> Tuple[bool, int]:
        try:
            value = int(raw)
        except ValueError:
            return False, 0
        if value < 0:
            return False, 0
        return True, value

    @staticmethod
    def _parse_int(raw: str) -> Tuple[bool, int]:
        try:
            return True, int(raw)
        except ValueError:
            return False, 0

    @staticmethod
    def _format_keys(keys: list) -> str:
        if not keys:
            return "(empty array)"
        lines = []
        index = 1
        for key in keys:
            lines.append(str(index) + '. "' + key + '"')
            index += 1
        return "\n".join(lines)

    def execute(self, line: str) -> Tuple[bool, str]:
        try:
            parts = shlex.split(line)
        except ValueError:
            return False, "(error) ERR invalid quoted string"

        if not parts:
            return False, ""

        raw_command = parts[0]
        command = raw_command.upper()

        if command in ("EXIT", "QUIT"):
            if len(parts) != 1:
                return False, self._wrong_args(command)
            return True, ""

        if command == "SET":
            if len(parts) != 3:
                return False, self._wrong_args(command)
            return False, self.store.set(parts[1], parts[2])

        if command == "GET":
            if len(parts) != 2:
                return False, self._wrong_args(command)
            return False, self.store.get(parts[1])

        if command == "DEL":
            if len(parts) != 2:
                return False, self._wrong_args(command)
            return False, self.store.delete(parts[1])

        if command == "EXISTS":
            if len(parts) != 2:
                return False, self._wrong_args(command)
            return False, self.store.exists(parts[1])

        if command == "DBSIZE":
            if len(parts) != 1:
                return False, self._wrong_args(command)
            return False, self.store.dbsize()

        if command == "KEYS":
            if len(parts) != 1:
                return False, self._wrong_args(command)
            return False, self._format_keys(self.store.keys())

        if command == "CONFIG":
            if len(parts) != 4 or parts[1].upper() != "SET" or parts[2].lower() != "maxmemory":
                return False, self._wrong_args(command)
            valid, value = self._parse_nonnegative_int(parts[3])
            if not valid:
                return False, self._integer_error()
            return False, self.store.config_set_maxmemory(value)

        if command == "INFO":
            if len(parts) != 2 or parts[1].lower() != "memory":
                return False, self._wrong_args(command)
            return False, self.store.info_memory()

        if command == "EXPIRE":
            if len(parts) != 3:
                return False, self._wrong_args(command)
            valid, seconds = self._parse_int(parts[2])
            if not valid:
                return False, self._integer_error()
            return False, self.store.expire(parts[1], seconds)

        if command == "TTL":
            if len(parts) != 2:
                return False, self._wrong_args(command)
            return False, self.store.ttl(parts[1])

        return False, "(error) ERR unknown command '" + raw_command + "'"


def run_repl() -> None:
    """Run the terminal read-eval-print loop until exit or quit."""
    processor = CommandProcessor(MiniRedis())
    while True:
        try:
            line = input("mini-redis> ")
        except EOFError:
            print()
            return
        should_exit, output = processor.execute(line)
        if output:
            print(output)
        if should_exit:
            return
