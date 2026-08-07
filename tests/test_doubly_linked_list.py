import unittest

from _support import SRC  # noqa: F401
from mini_redis.doubly_linked_list import DoublyLinkedList


class DoublyLinkedListTests(unittest.TestCase):
    def test_insert_remove_and_move_preserve_links(self):
        linked = DoublyLinkedList()
        a = linked.insert_back("a")
        b = linked.insert_back("b")
        c = linked.insert_front("c")

        self.assertEqual(linked.head.data, "c")
        self.assertEqual(linked.tail.data, "b")
        self.assertIs(linked.head.next, a)
        self.assertIs(a.prev, c)

        linked.move_to_front(b)
        self.assertEqual(linked.head.data, "b")
        self.assertEqual(linked.tail.data, "a")
        self.assertEqual(len(linked), 3)

        self.assertEqual(linked.remove_front(), "b")
        self.assertEqual(linked.remove_back(), "a")
        self.assertEqual(linked.remove_node(c), "c")
        self.assertEqual(len(linked), 0)
        self.assertIsNone(linked.head)
        self.assertIsNone(linked.tail)

    def test_empty_removals_are_safe(self):
        linked = DoublyLinkedList()
        self.assertIsNone(linked.remove_front())
        self.assertIsNone(linked.remove_back())


if __name__ == "__main__":
    unittest.main()
