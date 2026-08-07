"""Doubly linked list used by chaining buckets and the LRU queue."""

from typing import Any, Optional


class Node:
    """One doubly linked list node with prev, next, and data fields."""

    def __init__(self, data: Any) -> None:
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None
        self.data = data


class DoublyLinkedList:
    """Linked list whose insertion, removal, and node moves are O(1)."""

    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def insert_front(self, data: Any) -> Node:
        node = Node(data)
        node.next = self.head
        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node
        self._size += 1
        return node

    def insert_back(self, data: Any) -> Node:
        node = Node(data)
        node.prev = self.tail
        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node
        self.tail = node
        self._size += 1
        return node

    def remove_front(self) -> Any:
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self) -> Any:
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node: Node) -> Any:
        """Remove a known node in O(1) without scanning the list."""
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = None
        self._size -= 1
        return node.data

    def move_to_front(self, node: Node) -> None:
        """Move a known node to head in O(1)."""
        if node is self.head:
            return

        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        node.prev = None
        node.next = self.head
        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node
