"""Custom chained hash map with explicit hashing and resize logic."""

from typing import Any, List, Optional

from .doubly_linked_list import DoublyLinkedList, Node


class HashPair:
    """Key/value pair stored inside one chaining bucket."""

    def __init__(self, key: str, value: Any) -> None:
        self.key = key
        self.value = value


class HashMap:
    """Hash map using custom hashing, chaining, and 0.75 load-factor resize."""

    def __init__(self, capacity: int = 8) -> None:
        if capacity < 1:
            capacity = 1
        self._capacity = capacity
        self._buckets: List[Optional[DoublyLinkedList]] = [None] * capacity
        self._size = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def size(self) -> int:
        return self._size

    def _hash(self, key: str) -> int:
        """Return a bucket index using a small FNV-1a-style hash."""
        value = 2166136261
        for byte in key.encode("utf-8"):
            value ^= byte
            value = (value * 16777619) & 0xFFFFFFFF
        return value % self._capacity

    def _find_node(self, key: str) -> Optional[Node]:
        bucket = self._buckets[self._hash(key)]
        if bucket is None:
            return None
        node = bucket.head
        while node is not None:
            pair = node.data
            if pair.key == key:
                return node
            node = node.next
        return None

    def put(self, key: str, value: Any) -> Any:
        node = self._find_node(key)
        if node is not None:
            previous = node.data.value
            node.data.value = value
            return previous

        index = self._hash(key)
        bucket = self._buckets[index]
        if bucket is None:
            bucket = DoublyLinkedList()
            self._buckets[index] = bucket
        bucket.insert_back(HashPair(key, value))
        self._size += 1

        if self._size * 4 > self._capacity * 3:
            self._resize(self._capacity * 2)
        return None

    def get(self, key: str) -> Any:
        node = self._find_node(key)
        if node is None:
            return None
        return node.data.value

    def contains(self, key: str) -> bool:
        return self._find_node(key) is not None

    def remove(self, key: str) -> Any:
        index = self._hash(key)
        bucket = self._buckets[index]
        if bucket is None:
            return None

        node = bucket.head
        while node is not None:
            pair = node.data
            if pair.key == key:
                value = pair.value
                bucket.remove_node(node)
                self._size -= 1
                if len(bucket) == 0:
                    self._buckets[index] = None
                return value
            node = node.next
        return None

    def keys(self) -> List[str]:
        result: List[str] = []
        for bucket in self._buckets:
            if bucket is None:
                continue
            node = bucket.head
            while node is not None:
                result.append(node.data.key)
                node = node.next
        return result

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._capacity = new_capacity
        self._buckets = [None] * new_capacity
        old_size = self._size
        self._size = 0

        for bucket in old_buckets:
            if bucket is None:
                continue
            node = bucket.head
            while node is not None:
                pair = node.data
                self._insert_without_resize(pair.key, pair.value)
                node = node.next

        self._size = old_size

    def _insert_without_resize(self, key: str, value: Any) -> None:
        index = self._hash(key)
        bucket = self._buckets[index]
        if bucket is None:
            bucket = DoublyLinkedList()
            self._buckets[index] = bucket
        bucket.insert_back(HashPair(key, value))
        self._size += 1
