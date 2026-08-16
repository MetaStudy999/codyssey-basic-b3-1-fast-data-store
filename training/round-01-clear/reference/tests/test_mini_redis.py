import time
import unittest
from unittest.mock import patch

from mini_redis.cli import ERR_OOM, execute, repl
from mini_redis.doubly_linked_list import DoublyLinkedList
from mini_redis.hash_map import HashMap
from mini_redis.min_heap import MinHeap
from mini_redis.store import MiniRedis


class DoublyLinkedListTests(unittest.TestCase):
    def test_all_required_operations(self) -> None:
        linked = DoublyLinkedList()
        a = linked.insert_back("a")
        b = linked.insert_back("b")
        c = linked.insert_front("c")

        self.assertEqual(len(linked), 3)
        self.assertEqual(linked.head.next, c)
        self.assertEqual(linked.tail.prev, b)

        linked.move_to_front(b)
        self.assertEqual(linked.head.next, b)

        removed_front = linked.remove_front()
        self.assertIs(removed_front, b)
        self.assertIsNone(removed_front.prev)
        self.assertIsNone(removed_front.next)

        removed_node = linked.remove_node(a)
        self.assertIs(removed_node, a)
        self.assertEqual(len(linked), 1)

        removed_back = linked.remove_back()
        self.assertIs(removed_back, c)
        self.assertEqual(len(linked), 0)
        self.assertIsNone(linked.remove_front())
        self.assertIsNone(linked.remove_back())


class HashMapTests(unittest.TestCase):
    def test_put_get_remove_contains_keys_and_size(self) -> None:
        table = HashMap(initial_capacity=8)
        table.put("alpha", 1)
        table.put("beta", 2)
        table.put("gamma", 3)

        self.assertEqual(table.size(), 3)
        self.assertEqual(table.get("beta"), 2)
        self.assertTrue(table.contains("gamma"))
        self.assertIn("alpha", table.keys())
        self.assertEqual(table.remove("beta"), 2)
        self.assertFalse(table.contains("beta"))
        self.assertEqual(table.size(), 2)

    def test_chaining_collision_keeps_both_keys(self) -> None:
        table = HashMap(initial_capacity=8)
        keys = ["k{}".format(index) for index in range(100)]
        first = None
        second = None

        for left in range(len(keys)):
            for right in range(left + 1, len(keys)):
                if table._index(keys[left]) == table._index(keys[right]):
                    first = keys[left]
                    second = keys[right]
                    break
            if first is not None:
                break

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        table.put(first, "A")
        table.put(second, "B")
        self.assertEqual(table.get(first), "A")
        self.assertEqual(table.get(second), "B")
        self.assertEqual(table.size(), 2)

    def test_resize_only_after_load_factor_exceeds_point_75(self) -> None:
        table = HashMap(initial_capacity=8)
        for index in range(6):
            table.put("k{}".format(index), index)
        self.assertEqual(table.capacity(), 8)  # 6 / 8 == 0.75: no resize yet.

        table.put("k6", 6)  # 7 / 8 > 0.75: resize before insertion.
        self.assertEqual(table.capacity(), 16)
        for index in range(7):
            self.assertEqual(table.get("k{}".format(index)), index)


class MinHeapTests(unittest.TestCase):
    def test_push_pop_peek_size_and_minimum_order(self) -> None:
        heap = MinHeap()
        self.assertEqual(heap.size(), 0)
        heap.push((30.0, 1, "c"))
        heap.push((10.0, 1, "a"))
        heap.push((20.0, 1, "b"))
        heap.push((5.0, 1, "z"))

        self.assertEqual(heap.size(), 4)
        self.assertEqual(heap.peek()[2], "z")
        self.assertEqual([heap.pop()[2] for _ in range(4)], ["z", "a", "b", "c"])
        self.assertEqual(heap.size(), 0)
        self.assertIsNone(heap.peek())
        self.assertIsNone(heap.pop())


class MiniRedisTests(unittest.TestCase):
    def test_basic_string_commands(self) -> None:
        store = MiniRedis()
        store.set("name", "Alice")
        self.assertEqual(store.get("name"), "Alice")
        self.assertEqual(store.exists("name"), 1)
        self.assertEqual(store.dbsize(), 1)
        self.assertIn("name", store.keys())
        self.assertEqual(store.delete("name"), 1)
        self.assertEqual(store.delete("name"), 0)
        self.assertIsNone(store.get("name"))

    def test_maxmemory_zero_is_unlimited(self) -> None:
        store = MiniRedis()
        store.configure_maxmemory(0)
        store.set("large", "x" * 10000)
        self.assertEqual(store.get("large"), "x" * 10000)
        self.assertEqual(store.memory_info()[1], 0)
        self.assertEqual(store.memory_info()[2], 0)

    def test_utf8_used_memory_and_overwrite_accounting(self) -> None:
        store = MiniRedis()
        store.set("한", "글")
        expected = len("한".encode("utf-8")) + len("글".encode("utf-8"))
        self.assertEqual(store.memory_info()[0], expected)

        store.set("한", "글글")
        expected = len("한".encode("utf-8")) + len("글글".encode("utf-8"))
        used, maximum, evicted = store.memory_info()
        self.assertEqual(used, expected)
        self.assertEqual(maximum, 0)
        self.assertEqual(evicted, 0)

    def test_lru_eviction_after_successful_get(self) -> None:
        store = MiniRedis()
        store.configure_maxmemory(6)
        store.set("a", "1")       # 2 bytes
        store.set("b", "22")      # 3 bytes, b MRU / a LRU
        self.assertEqual(store.get("a"), "1")  # a MRU / b LRU
        store.set("c", "33")      # +3 -> 8, evict b -> 5
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("a"), "1")
        self.assertEqual(store.get("c"), "33")
        self.assertEqual(store.memory_info()[2], 1)

    def test_overwrite_is_successful_set_and_refreshes_lru(self) -> None:
        store = MiniRedis()
        store.configure_maxmemory(6)
        store.set("a", "1")
        store.set("b", "22")
        store.set("a", "1")  # overwrite must make a MRU.
        store.set("c", "33")
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.get("a"), "1")
        self.assertEqual(store.get("c"), "33")

    def test_single_entry_oom_preserves_existing_data(self) -> None:
        store = MiniRedis()
        store.configure_maxmemory(3)
        store.set("a", "1")
        result = execute(store, "SET long value")
        self.assertEqual(result, ERR_OOM)
        self.assertEqual(store.dbsize(), 1)
        self.assertEqual(store.get("a"), "1")
        self.assertEqual(store.memory_info()[2], 0)

    def test_eviction_repeats_until_within_limit(self) -> None:
        store = MiniRedis()
        store.set("a", "1")
        store.set("b", "2")
        store.set("c", "3")
        store.configure_maxmemory(4)
        store.set("d", "4")
        used, maximum, evicted = store.memory_info()
        self.assertLessEqual(used, maximum)
        self.assertGreaterEqual(evicted, 2)

    def test_expire_ttl_and_immediate_expire(self) -> None:
        store = MiniRedis()
        store.set("temp", "value")
        self.assertEqual(store.ttl("temp"), -1)
        self.assertEqual(store.expire("temp", 10), 1)
        self.assertGreater(store.ttl("temp"), 0)

        entry = store.store.get("temp")
        entry.expire_at = time.time() - 1
        self.assertIsNone(store.get("temp"))
        self.assertEqual(store.ttl("temp"), -2)

        store.set("now", "x")
        self.assertEqual(store.expire("now", 0), 1)
        self.assertEqual(store.exists("now"), 0)
        self.assertEqual(store.expire("missing", 10), 0)

    def test_expire_reset_uses_lazy_deletion_without_deleting_current_ttl(self) -> None:
        store = MiniRedis()
        with patch("mini_redis.store.time.time", return_value=100.0):
            store.set("k", "v")
            self.assertEqual(store.expire("k", 10), 1)  # stale heap item at 110

        with patch("mini_redis.store.time.time", return_value=105.0):
            self.assertEqual(store.expire("k", 20), 1)  # current TTL at 125

        with patch("mini_redis.store.time.time", return_value=111.0):
            self.assertEqual(store.dbsize(), 1)  # stale 110 item must be ignored.
            self.assertEqual(store.get("k"), "v")
            self.assertGreater(store.ttl("k"), 0)

    def test_delete_invalidates_old_ttl_before_same_key_is_reinserted(self) -> None:
        store = MiniRedis()
        with patch("mini_redis.store.time.time", return_value=100.0):
            store.set("k", "old")
            store.expire("k", 10)
            self.assertEqual(store.delete("k"), 1)
            store.set("k", "new")

        with patch("mini_redis.store.time.time", return_value=111.0):
            self.assertEqual(store.dbsize(), 1)
            self.assertEqual(store.get("k"), "new")
            self.assertEqual(store.ttl("k"), -1)

    def test_overwrite_resets_ttl_and_invalidates_old_heap_item(self) -> None:
        store = MiniRedis()
        with patch("mini_redis.store.time.time", return_value=100.0):
            store.set("k", "v1")
            store.expire("k", 10)
            store.set("k", "v2")
            self.assertEqual(store.ttl("k"), -1)

        with patch("mini_redis.store.time.time", return_value=111.0):
            self.assertEqual(store.get("k"), "v2")
            self.assertEqual(store.ttl("k"), -1)

    def test_expired_key_is_missing_for_key_commands_and_global_views(self) -> None:
        store = MiniRedis()
        with patch("mini_redis.store.time.time", return_value=100.0):
            store.set("gone", "x")
            store.expire("gone", 5)

        with patch("mini_redis.store.time.time", return_value=106.0):
            self.assertIsNone(store.get("gone"))
            self.assertEqual(store.exists("gone"), 0)
            self.assertEqual(store.delete("gone"), 0)
            self.assertEqual(store.ttl("gone"), -2)
            self.assertEqual(store.dbsize(), 0)
            self.assertNotIn("gone", store.keys())
            self.assertEqual(store.memory_info()[0], 0)

    def test_delete_removes_memory_and_lru_entry(self) -> None:
        store = MiniRedis()
        store.set("key", "value")
        self.assertGreater(store.used_memory, 0)
        self.assertEqual(store.delete("key"), 1)
        self.assertEqual(store.used_memory, 0)
        self.assertEqual(len(store.lru), 0)


class CliTests(unittest.TestCase):
    def test_cli_string_commands_and_quoted_value(self) -> None:
        store = MiniRedis()
        self.assertEqual(execute(store, 'SET name "Alice Kim"'), "OK")
        self.assertEqual(execute(store, "get name"), '"Alice Kim"')
        self.assertEqual(execute(store, "EXISTS name"), "(integer) 1")
        self.assertEqual(execute(store, "DBSIZE"), "(integer) 1")
        self.assertIn('"name"', execute(store, "KEYS"))
        self.assertEqual(execute(store, "DEL name"), "(integer) 1")
        self.assertEqual(execute(store, "GET name"), "(nil)")

    def test_cli_error_contract(self) -> None:
        store = MiniRedis()
        self.assertEqual(execute(store, "GET"), "(error) ERR wrong number of arguments for 'GET' command")
        self.assertEqual(execute(store, "HELLO"), "(error) ERR unknown command 'HELLO'")
        self.assertEqual(execute(store, "CONFIG SET maxmemory abc"), "(error) ERR value is not an integer or out of range")
        self.assertEqual(execute(store, "CONFIG SET maxmemory -1"), "(error) ERR value is not an integer or out of range")
        self.assertEqual(execute(store, "CONFIG GET maxmemory 1"), "(error) ERR syntax error")
        self.assertEqual(execute(store, "INFO stats"), "(error) ERR syntax error")
        self.assertEqual(execute(store, 'SET broken "quote'), "(error) ERR syntax error")

    def test_memory_info_and_ttl_commands(self) -> None:
        store = MiniRedis()
        self.assertEqual(execute(store, "CONFIG SET maxmemory 100"), "OK")
        info = execute(store, "INFO memory")
        self.assertIn("used_memory:0", info)
        self.assertIn("maxmemory:100", info)
        self.assertIn("evicted_keys:0", info)
        self.assertEqual(execute(store, "SET a 1"), "OK")
        self.assertEqual(execute(store, "EXPIRE a 10"), "(integer) 1")
        self.assertTrue(execute(store, "TTL a").startswith("(integer) "))
        self.assertEqual(execute(store, "EXPIRE missing 10"), "(integer) 0")
        self.assertEqual(execute(store, "TTL missing"), "(integer) -2")

    def test_repl_quit_path(self) -> None:
        with patch("builtins.input", side_effect=["quit"]):
            repl()


if __name__ == "__main__":
    unittest.main()
