"""Small binary min-heap for TTL expiration records."""

from typing import Any, List


class MinHeap:
    """Array-backed minimum heap with explicit heapify operations."""

    def __init__(self) -> None:
        self._items: List[Any] = []

    def size(self) -> int:
        return len(self._items)

    def peek(self) -> Any:
        if not self._items:
            return None
        return self._items[0]

    def push(self, item: Any) -> None:
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def pop(self) -> Any:
        if not self._items:
            return None
        minimum = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._heapify_down(0)
        return minimum

    def _heapify_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._items[parent] <= self._items[index]:
                break
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def _heapify_down(self, index: int) -> None:
        length = len(self._items)
        while True:
            left = index * 2 + 1
            right = left + 1
            smallest = index

            if left < length and self._items[left] < self._items[smallest]:
                smallest = left
            if right < length and self._items[right] < self._items[smallest]:
                smallest = right
            if smallest == index:
                return

            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest
