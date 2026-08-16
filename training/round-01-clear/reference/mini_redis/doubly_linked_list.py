from typing import Any, Optional


class Node:
    def __init__(self, data: Any = None) -> None:
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None
        self.data = data


class DoublyLinkedList:
    """O(1) insert/remove/move operations using head/tail sentinels."""

    def __init__(self) -> None:
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert_front(self, data: Any) -> Node:
        node = Node(data)
        self._insert_between(node, self.head, self.head.next)
        return node

    def insert_back(self, data: Any) -> Node:
        node = Node(data)
        self._insert_between(node, self.tail.prev, self.tail)
        return node

    def remove_front(self) -> Optional[Node]:
        if self._size == 0:
            return None
        return self.remove_node(self.head.next)

    def remove_back(self) -> Optional[Node]:
        if self._size == 0:
            return None
        return self.remove_node(self.tail.prev)

    def remove_node(self, node: Optional[Node]) -> Optional[Node]:
        if node is None or node is self.head or node is self.tail:
            return None
        if node.prev is None or node.next is None:
            return None
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1
        return node

    def move_to_front(self, node: Optional[Node]) -> None:
        if node is None or node is self.head or node is self.tail:
            return
        if node.prev is self.head:
            return
        if node.prev is None or node.next is None:
            return
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1
        self._insert_between(node, self.head, self.head.next)

    def back(self) -> Optional[Node]:
        if self._size == 0:
            return None
        return self.tail.prev

    def _insert_between(self, node: Node, left: Node, right: Optional[Node]) -> None:
        if right is None:
            raise RuntimeError("invalid list state")
        node.prev = left
        node.next = right
        left.next = node
        right.prev = node
        self._size += 1
