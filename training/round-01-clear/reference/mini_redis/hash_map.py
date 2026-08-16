from typing import Any, List, Optional


class _BucketNode:
    def __init__(self, key: str, value: Any, next_node: Optional["_BucketNode"] = None) -> None:
        self.key = key
        self.value = value
        self.next = next_node


class HashMap:
    """Chaining hash map with a custom hash function and 0.75 resize threshold."""

    def __init__(self, initial_capacity: int = 8) -> None:
        if initial_capacity < 1:
            initial_capacity = 1
        self._buckets: List[Optional[_BucketNode]] = [None] * initial_capacity
        self._size = 0

    def _hash(self, key: str) -> int:
        # FNV-1a style 64-bit rolling hash, implemented directly for learning.
        value = 1469598103934665603
        for byte in key.encode("utf-8"):
            value ^= byte
            value = (value * 1099511628211) & 0xFFFFFFFFFFFFFFFF
        return value

    def _index(self, key: str) -> int:
        return self._hash(key) % len(self._buckets)

    def put(self, key: str, value: Any) -> Optional[Any]:
        index = self._index(key)
        node = self._buckets[index]
        while node is not None:
            if node.key == key:
                old = node.value
                node.value = value
                return old
            node = node.next

        if (self._size + 1) / float(len(self._buckets)) > 0.75:
            self._resize(len(self._buckets) * 2)
            index = self._index(key)

        self._buckets[index] = _BucketNode(key, value, self._buckets[index])
        self._size += 1
        return None

    def get(self, key: str) -> Optional[Any]:
        node = self._buckets[self._index(key)]
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next
        return None

    def remove(self, key: str) -> Optional[Any]:
        index = self._index(key)
        node = self._buckets[index]
        prev: Optional[_BucketNode] = None
        while node is not None:
            if node.key == key:
                if prev is None:
                    self._buckets[index] = node.next
                else:
                    prev.next = node.next
                self._size -= 1
                return node.value
            prev = node
            node = node.next
        return None

    def contains(self, key: str) -> bool:
        node = self._buckets[self._index(key)]
        while node is not None:
            if node.key == key:
                return True
            node = node.next
        return False

    def keys(self) -> List[str]:
        result: List[str] = []
        for bucket in self._buckets:
            node = bucket
            while node is not None:
                result.append(node.key)
                node = node.next
        return result

    def size(self) -> int:
        return self._size

    def capacity(self) -> int:
        return len(self._buckets)

    def _resize(self, new_capacity: int) -> None:
        old_buckets = self._buckets
        self._buckets = [None] * new_capacity

        for bucket in old_buckets:
            node = bucket
            while node is not None:
                next_node = node.next
                index = self._index(node.key)
                node.next = self._buckets[index]
                self._buckets[index] = node
                node = next_node
