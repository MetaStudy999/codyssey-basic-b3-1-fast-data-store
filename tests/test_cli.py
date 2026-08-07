import unittest

from _support import FakeClock, SRC  # noqa: F401
from mini_redis.cli import CommandProcessor
from mini_redis.store import MiniRedis


class CommandProcessorTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.processor = CommandProcessor(MiniRedis(clock=self.clock))

    def run_command(self, line):
        should_exit, output = self.processor.execute(line)
        self.assertFalse(should_exit)
        return output

    def test_case_insensitive_commands_and_quoted_value(self):
        self.assertEqual(self.run_command('set user:1 "Alice Smith"'), "OK")
        self.assertEqual(self.run_command("GeT user:1"), '"Alice Smith"')

    def test_key_listing_and_info(self):
        self.run_command("SET a 1")
        output = self.run_command("KEYS")
        self.assertIn('1. "a"', output)
        info = self.run_command("INFO memory")
        self.assertIn("used_memory:2", info)
        self.assertIn("maxmemory:0", info)
        self.assertIn("evicted_keys:0", info)

    def test_standard_errors(self):
        self.assertEqual(
            self.run_command("HELLO"),
            "(error) ERR unknown command 'HELLO'",
        )
        self.assertEqual(
            self.run_command("GET"),
            "(error) ERR wrong number of arguments for 'GET' command",
        )
        self.assertEqual(
            self.run_command("CONFIG SET maxmemory abc"),
            "(error) ERR value is not an integer or out of range",
        )
        self.assertEqual(
            self.run_command("CONFIG SET maxmemory -1"),
            "(error) ERR value is not an integer or out of range",
        )
        self.assertEqual(
            self.run_command("EXPIRE a nope"),
            "(error) ERR value is not an integer or out of range",
        )

    def test_oom_error(self):
        self.assertEqual(self.run_command("CONFIG SET maxmemory 2"), "OK")
        result = self.run_command("SET abc xyz")
        self.assertTrue(result.startswith("(error) OOM"))

    def test_exit_and_quit(self):
        should_exit, output = self.processor.execute("exit")
        self.assertTrue(should_exit)
        self.assertEqual(output, "")
        should_exit, _ = self.processor.execute("QUIT")
        self.assertTrue(should_exit)


if __name__ == "__main__":
    unittest.main()
