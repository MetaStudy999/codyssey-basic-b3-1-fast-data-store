from typing import List, Optional, Tuple

HeapItem = Tuple[float, int, str]


class MinHeap:
    """Minimum heap for (expire_at, ttl_version, key) items."""

    def __init__(self) -> None:
        self._items: List[HeapItem] = []

    def push(self, item: HeapItem) -> None:
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def pop(self) -> Optional[HeapItem]:
        if not self._items:
            return None
        if len(self._items) == 1:
            return self._items.pop()
        root = self._items[0]
        self._items[0] = self._items.pop()
        self._heapify_down(0)
        return root

    def peek(self) -> Optional[HeapItem]:
        if not self._items:
            return None
        return self._items[0]

    def size(self) -> int:
        return len(self._items)

    def _heapify_up(self, index: int) -> None:
        while index > 0:
            parent = (index - 1) // 2
            if self._items[parent] <= self._items[index]:
                return
            self._items[parent], self._items[index] = self._items[index], self._items[parent]
            index = parent

    def _heapify_down(self, index: int) -> None:
        size = len(self._items)
        while True:
            left = index * 2 + 1
            right = left + 1
            smallest = index

            if left < size and self._items[left] < self._items[smallest]:
                smallest = left
            if right < size and self._items[right] < self._items[smallest]:
                smallest = right
            if smallest == index:
                return

            self._items[index], self._items[smallest] = self._items[smallest], self._items[index]
            index = smallest
