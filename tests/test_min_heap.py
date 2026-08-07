import unittest

from _support import SRC  # noqa: F401
from mini_redis.min_heap import MinHeap


class MinHeapTests(unittest.TestCase):
    def test_heap_orders_expiry_tuples(self):
        heap = MinHeap()
        heap.push((30.0, "c"))
        heap.push((10.0, "a"))
        heap.push((20.0, "b"))
        self.assertEqual(heap.peek(), (10.0, "a"))
        self.assertEqual(heap.pop(), (10.0, "a"))
        self.assertEqual(heap.pop(), (20.0, "b"))
        self.assertEqual(heap.pop(), (30.0, "c"))
        self.assertIsNone(heap.pop())
        self.assertIsNone(heap.peek())
        self.assertEqual(heap.size(), 0)


if __name__ == "__main__":
    unittest.main()
