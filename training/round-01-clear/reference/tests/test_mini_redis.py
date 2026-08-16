import time
import unittest

from mini_redis.cli import ERR_OOM, execute
from mini_redis.doubly_linked_list import DoublyLinkedList
from mini_redis.hash_map import HashMap
from mini_redis.min_heap import MinHeap
from mini_redis.store import MiniRedis


class DoublyLinkedListTests(unittest.TestCase):
    def test_insert_remove_and_move(self) -> None:
        linked = DoublyLinkedList()
        a = linked.insert_back("a")
        b = linked.insert_back("b")
        linked.insert_front("c")
        self.assertEqual(len(linked), 3)
        linked.move_to_front(b)
        self.assertEqual(linked.head.next.data, "b")
        linked.remove_node(a)
        self.assertEqual(len(linked), 2)
        self.assertEqual(linked.remove_back().data, "c")


class HashMapTests(unittest.TestCase):
    def test_put_get_remove_contains_keys_and_resize(self) -> None:
        table = HashMap(initial_capacity=2)
        for index in range(20):
            table.put("k{}".format(index), index)
        self.assertEqual(table.size(), 20)
        self.assertGreaterEqual(table.capacity(), 32)
        self.assertEqual(table.get("k7"), 7)
        self.assertTrue(table.contains("k19"))
        self.assertIn("k3", table.keys())
        self.assertEqual(table.remove("k7"), 7)
        self.assertFalse(table.contains("k7"))


class MinHeapTests(unittest.TestCase):
    def test_minimum_order(self) -> None:
        heap = MinHeap()
        heap.push((30.0, 1, "c"))
        heap.push((10.0, 1, "a"))
        heap.push((20.0, 1, "b"))
        self.assertEqual(heap.peek()[2], "a")
        self.assertEqual(heap.pop()[2], "a")
        self.assertEqual(heap.pop()[2], "b")
        self.assertEqual(heap.pop()[2], "c")
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

    def test_utf8_used_memory(self) -> None:
        store = MiniRedis()
        store.set("한", "글")
        used, maximum, evicted = store.memory_info()
        self.assertEqual(used, len("한".encode("utf-8")) + len("글".encode("utf-8")))
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

    def test_single_entry_oom_does_not_store(self) -> None:
        store = MiniRedis()
        store.configure_maxmemory(3)
        result = execute(store, "SET long value")
        self.assertEqual(result, ERR_OOM)
        self.assertEqual(store.dbsize(), 0)

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

    def test_overwrite_resets_ttl(self) -> None:
        store = MiniRedis()
        store.set("k", "v1")
        store.expire("k", 30)
        store.set("k", "v2")
        self.assertEqual(store.get("k"), "v2")
        self.assertEqual(store.ttl("k"), -1)

    def test_delete_removes_memory_and_lru_entry(self) -> None:
        store = MiniRedis()
        store.set("key", "value")
        self.assertGreater(store.used_memory, 0)
        self.assertEqual(store.delete("key"), 1)
        self.assertEqual(store.used_memory, 0)
        self.assertEqual(len(store.lru), 0)


class CliTests(unittest.TestCase):
    def test_cli_and_errors(self) -> None:
        store = MiniRedis()
        self.assertEqual(execute(store, 'SET name "Alice Kim"'), "OK")
        self.assertEqual(execute(store, "GET name"), '"Alice Kim"')
        self.assertEqual(execute(store, "GET"), "(error) ERR wrong number of arguments for 'GET' command")
        self.assertEqual(execute(store, "HELLO"), "(error) ERR unknown command 'HELLO'")
        self.assertEqual(execute(store, "CONFIG SET maxmemory abc"), "(error) ERR value is not an integer or out of range")

    def test_memory_info_and_ttl_commands(self) -> None:
        store = MiniRedis()
        self.assertEqual(execute(store, "CONFIG SET maxmemory 100"), "OK")
        self.assertIn("maxmemory:100", execute(store, "INFO memory"))
        self.assertEqual(execute(store, "SET a 1"), "OK")
        self.assertEqual(execute(store, "EXPIRE a 10"), "(integer) 1")
        self.assertTrue(execute(store, "TTL a").startswith("(integer) "))


if __name__ == "__main__":
    unittest.main()
