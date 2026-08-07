import unittest

from _support import FakeClock, SRC  # noqa: F401
from mini_redis.store import MiniRedis


class MiniRedisStoreTests(unittest.TestCase):
    def test_basic_string_commands(self):
        store = MiniRedis()
        self.assertEqual(store.set("name", "Alice"), "OK")
        self.assertEqual(store.get("name"), '"Alice"')
        self.assertEqual(store.exists("name"), "(integer) 1")
        self.assertEqual(store.dbsize(), "(integer) 1")
        self.assertIn("name", store.keys())
        self.assertEqual(store.delete("name"), "(integer) 1")
        self.assertEqual(store.delete("name"), "(integer) 0")
        self.assertEqual(store.get("name"), "(nil)")

    def test_lru_updates_on_set_and_successful_get(self):
        store = MiniRedis()
        store.set("a", "1")
        store.set("b", "2")
        store.set("c", "3")
        self.assertEqual(store.lru_keys_mru_to_lru(), ["c", "b", "a"])
        store.get("a")
        self.assertEqual(store.lru_keys_mru_to_lru(), ["a", "c", "b"])

    def test_memory_limit_evicts_lru_and_counts_utf8_bytes(self):
        store = MiniRedis()
        self.assertEqual(store.config_set_maxmemory(6), "OK")
        self.assertEqual(store.set("a", "11"), "OK")
        self.assertEqual(store.set("b", "22"), "OK")
        store.get("a")
        self.assertEqual(store.set("c", "33"), "OK")
        self.assertEqual(store.get("b"), "(nil)")
        self.assertEqual(store.get("a"), '"11"')
        self.assertEqual(store.used_memory, 6)
        self.assertEqual(store.evicted_keys, 1)
        self.assertIn("used_memory:6", store.info_memory())

        unicode_store = MiniRedis()
        unicode_store.set("가", "나")
        self.assertEqual(unicode_store.used_memory, 6)

    def test_single_entry_larger_than_limit_is_rejected_without_overwrite(self):
        store = MiniRedis()
        store.set("a", "1")
        store.config_set_maxmemory(3)
        result = store.set("a", "toolong")
        self.assertTrue(result.startswith("(error) OOM"))
        self.assertEqual(store.get("a"), '"1"')

    def test_ttl_countdown_expiry_and_missing_codes(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("token", "abc")
        self.assertEqual(store.ttl("token"), "(integer) -1")
        self.assertEqual(store.expire("token", 3), "(integer) 1")
        self.assertEqual(store.ttl("token"), "(integer) 3")
        clock.advance(2)
        self.assertEqual(store.ttl("token"), "(integer) 1")
        clock.advance(1)
        self.assertEqual(store.get("token"), "(nil)")
        self.assertEqual(store.ttl("token"), "(integer) -2")
        self.assertEqual(store.dbsize(), "(integer) 0")

    def test_expired_get_does_not_touch_remaining_lru_order(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("a", "1")
        store.set("b", "2")
        store.expire("a", 1)
        self.assertEqual(store.lru_keys_mru_to_lru(), ["b", "a"])
        clock.advance(1)
        self.assertEqual(store.get("a"), "(nil)")
        self.assertEqual(store.lru_keys_mru_to_lru(), ["b"])

    def test_overwrite_resets_ttl_and_lazy_heap_record_is_harmless(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("a", "1")
        store.expire("a", 2)
        store.set("a", "2")
        self.assertIsNone(store.active_ttl("a"))
        self.assertEqual(store.ttl("a"), "(integer) -1")
        clock.advance(5)
        self.assertEqual(store.get("a"), '"2"')

    def test_delete_removes_data_lru_and_active_ttl(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("a", "1")
        store.expire("a", 10)
        self.assertEqual(store.delete("a"), "(integer) 1")
        self.assertIsNone(store.active_ttl("a"))
        self.assertEqual(store.lru_keys_mru_to_lru(), [])
        self.assertEqual(store.dbsize(), "(integer) 0")
        clock.advance(20)
        self.assertEqual(store.dbsize(), "(integer) 0")

    def test_expire_missing_and_nonpositive_immediate_delete(self):
        store = MiniRedis()
        self.assertEqual(store.expire("missing", 5), "(integer) 0")
        store.set("a", "1")
        self.assertEqual(store.expire("a", 0), "(integer) 1")
        self.assertEqual(store.exists("a"), "(integer) 0")

    def test_dbsize_and_keys_purge_expired_without_get(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("old", "1")
        store.set("live", "2")
        store.expire("old", 1)
        clock.advance(2)
        self.assertEqual(store.dbsize(), "(integer) 1")
        self.assertEqual(store.keys(), ["live"])


if __name__ == "__main__":
    unittest.main()
