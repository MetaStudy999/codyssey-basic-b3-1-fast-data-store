import unittest

from _support import SRC  # noqa: F401
from mini_redis.hash_map import HashMap


class HashMapTests(unittest.TestCase):
    def _find_collision(self, table):
        seen = []
        index = 0
        while index < 500:
            key = "k" + str(index)
            bucket = table._hash(key)
            for existing_key, existing_bucket in seen:
                if existing_bucket == bucket and existing_key != key:
                    return existing_key, key
            seen.append((key, bucket))
            index += 1
        self.fail("could not construct a collision")

    def test_collision_chaining_preserves_values(self):
        table = HashMap(capacity=4)
        first, second = self._find_collision(table)
        table.put(first, "one")
        table.put(second, "two")
        self.assertEqual(table.get(first), "one")
        self.assertEqual(table.get(second), "two")
        self.assertEqual(table.size(), 2)

    def test_resize_doubles_capacity_and_preserves_entries(self):
        table = HashMap(capacity=4)
        table.put("a", 1)
        table.put("b", 2)
        table.put("c", 3)
        self.assertEqual(table.capacity, 4)
        table.put("d", 4)
        self.assertEqual(table.capacity, 8)
        self.assertEqual(table.size(), 4)
        self.assertEqual(table.get("a"), 1)
        self.assertEqual(table.get("d"), 4)

    def test_update_remove_contains_and_keys(self):
        table = HashMap()
        self.assertIsNone(table.put("x", 1))
        self.assertEqual(table.put("x", 2), 1)
        self.assertTrue(table.contains("x"))
        self.assertIn("x", table.keys())
        self.assertEqual(table.remove("x"), 2)
        self.assertFalse(table.contains("x"))
        self.assertIsNone(table.remove("missing"))


if __name__ == "__main__":
    unittest.main()
