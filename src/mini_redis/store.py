"""Mini Redis core that combines custom structures into LRU/TTL behavior."""

import time
from typing import Callable, List, Optional

from .doubly_linked_list import DoublyLinkedList, Node
from .hash_map import HashMap
from .min_heap import MinHeap


class Entry:
    """Stored string value plus its known O(1) LRU list node."""

    def __init__(self, key: str, value: str, lru_node: Node) -> None:
        self.key = key
        self.value = value
        self.lru_node = lru_node


class MiniRedis:
    """In-memory string store with LRU eviction and heap-based TTL expiry."""

    def __init__(self, clock: Optional[Callable[[], float]] = None) -> None:
        self._data = HashMap()
        self._lru = DoublyLinkedList()
        self._ttl_by_key = HashMap()
        self._expiry_heap = MinHeap()
        self._clock = clock if clock is not None else time.time
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    @staticmethod
    def _memory_cost(key: str, value: str) -> int:
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _active_expiry(self, key: str) -> Optional[float]:
        expiry = self._ttl_by_key.get(key)
        if expiry is None:
            return None
        return float(expiry)

    def _expire_if_needed(self, key: str) -> bool:
        expiry = self._active_expiry(key)
        if expiry is None or expiry > self._clock():
            return False
        self._delete_key(key, count_eviction=False)
        return True

    def _purge_expired(self) -> None:
        now = self._clock()
        while self._expiry_heap.size() > 0:
            record = self._expiry_heap.peek()
            expire_at = float(record[0])
            key = str(record[1])

            active = self._active_expiry(key)
            if active is None or active != expire_at:
                self._expiry_heap.pop()
                continue
            if expire_at > now:
                return

            self._expiry_heap.pop()
            self._delete_key(key, count_eviction=False)

    def _delete_key(self, key: str, count_eviction: bool) -> bool:
        entry = self._data.remove(key)
        if entry is None:
            self._ttl_by_key.remove(key)
            return False

        self._lru.remove_node(entry.lru_node)
        self._ttl_by_key.remove(key)
        self.used_memory -= self._memory_cost(key, entry.value)
        if self.used_memory < 0:
            self.used_memory = 0
        if count_eviction:
            self.evicted_keys += 1
        return True

    def _evict_to_limit(self) -> None:
        if self.maxmemory == 0:
            return
        self._purge_expired()
        while self.used_memory > self.maxmemory and self._lru.tail is not None:
            key = str(self._lru.tail.data)
            self._delete_key(key, count_eviction=True)

    def set(self, key: str, value: str) -> str:
        self._expire_if_needed(key)
        new_cost = self._memory_cost(key, value)
        if self.maxmemory > 0 and new_cost > self.maxmemory:
            return "(error) OOM command not allowed when used_memory > 'maxmemory'"

        entry = self._data.get(key)
        if entry is None:
            node = self._lru.insert_front(key)
            entry = Entry(key, value, node)
            self._data.put(key, entry)
            self.used_memory += new_cost
        else:
            self.used_memory -= self._memory_cost(key, entry.value)
            entry.value = value
            self.used_memory += new_cost
            self._lru.move_to_front(entry.lru_node)

        self._ttl_by_key.remove(key)
        self._evict_to_limit()
        return "OK"

    def get(self, key: str) -> str:
        if self._expire_if_needed(key):
            return "(nil)"
        entry = self._data.get(key)
        if entry is None:
            return "(nil)"
        self._lru.move_to_front(entry.lru_node)
        return '"' + entry.value + '"'

    def delete(self, key: str) -> str:
        self._expire_if_needed(key)
        deleted = self._delete_key(key, count_eviction=False)
        return "(integer) 1" if deleted else "(integer) 0"

    def exists(self, key: str) -> str:
        if self._expire_if_needed(key):
            return "(integer) 0"
        return "(integer) 1" if self._data.contains(key) else "(integer) 0"

    def dbsize(self) -> str:
        self._purge_expired()
        return "(integer) " + str(self._data.size())

    def keys(self) -> List[str]:
        self._purge_expired()
        return self._data.keys()

    def config_set_maxmemory(self, value: int) -> str:
        if value < 0:
            return "(error) ERR value is not an integer or out of range"
        self.maxmemory = value
        return "OK"

    def info_memory(self) -> str:
        self._purge_expired()
        return (
            "used_memory:" + str(self.used_memory) + "\n"
            "maxmemory:" + str(self.maxmemory) + "\n"
            "evicted_keys:" + str(self.evicted_keys)
        )

    def expire(self, key: str, seconds: int) -> str:
        self._expire_if_needed(key)
        if not self._data.contains(key):
            return "(integer) 0"
        if seconds <= 0:
            self._delete_key(key, count_eviction=False)
            return "(integer) 1"

        expire_at = self._clock() + seconds
        self._ttl_by_key.put(key, expire_at)
        self._expiry_heap.push((expire_at, key))
        return "(integer) 1"

    def ttl(self, key: str) -> str:
        if self._expire_if_needed(key):
            return "(integer) -2"
        if not self._data.contains(key):
            return "(integer) -2"
        expire_at = self._active_expiry(key)
        if expire_at is None:
            return "(integer) -1"
        remaining = int(expire_at - self._clock())
        if remaining < 0:
            remaining = 0
        return "(integer) " + str(remaining)

    def lru_keys_mru_to_lru(self) -> List[str]:
        """Testing/learning helper exposing LRU order without mutating it."""
        result: List[str] = []
        node = self._lru.head
        while node is not None:
            result.append(str(node.data))
            node = node.next
        return result

    def active_ttl(self, key: str) -> Optional[float]:
        """Testing helper: return the active TTL mapping, excluding lazy heap entries."""
        return self._active_expiry(key)
