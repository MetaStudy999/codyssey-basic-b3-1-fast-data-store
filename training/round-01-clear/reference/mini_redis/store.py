import math
import time
from typing import List, Optional, Tuple

from .doubly_linked_list import DoublyLinkedList, Node
from .hash_map import HashMap
from .min_heap import MinHeap


class OOMError(Exception):
    pass


class CacheEntry:
    def __init__(self, key: str, value: str, lru_node: Node) -> None:
        self.key = key
        self.value = value
        self.lru_node = lru_node
        self.expire_at: Optional[float] = None
        self.ttl_version = 0


class MiniRedis:
    def __init__(self) -> None:
        self.store = HashMap()
        self.lru = DoublyLinkedList()
        self.expirations = MinHeap()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    @staticmethod
    def _entry_bytes(key: str, value: str) -> int:
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _delete_key(self, key: str, eviction: bool = False) -> bool:
        entry = self.store.remove(key)
        if entry is None:
            return False
        self.lru.remove_node(entry.lru_node)
        self.used_memory -= self._entry_bytes(entry.key, entry.value)
        if self.used_memory < 0:
            self.used_memory = 0
        entry.ttl_version += 1
        entry.expire_at = None
        if eviction:
            self.evicted_keys += 1
        return True

    def _expire_if_needed(self, key: str, now: Optional[float] = None) -> bool:
        entry = self.store.get(key)
        if entry is None or entry.expire_at is None:
            return False
        current = time.time() if now is None else now
        if entry.expire_at <= current:
            self._delete_key(key)
            return True
        return False

    def _purge_expired(self, now: Optional[float] = None) -> None:
        current = time.time() if now is None else now
        while self.expirations.size() > 0:
            item = self.expirations.peek()
            if item is None or item[0] > current:
                return
            expire_at, version, key = self.expirations.pop()  # type: ignore[misc]
            entry = self.store.get(key)
            if entry is None:
                continue
            if entry.ttl_version != version:
                continue
            if entry.expire_at != expire_at:
                continue
            if expire_at <= current:
                self._delete_key(key)

    def _evict_lru(self) -> bool:
        node = self.lru.back()
        if node is None:
            return False
        key = str(node.data)
        return self._delete_key(key, eviction=True)

    def set(self, key: str, value: str) -> None:
        self._purge_expired()
        incoming_size = self._entry_bytes(key, value)
        if self.maxmemory > 0 and incoming_size > self.maxmemory:
            raise OOMError("single entry exceeds maxmemory")

        entry = self.store.get(key)
        if entry is None:
            node = self.lru.insert_front(key)
            entry = CacheEntry(key, value, node)
            self.store.put(key, entry)
            self.used_memory += incoming_size
        else:
            self.used_memory -= self._entry_bytes(entry.key, entry.value)
            entry.value = value
            entry.ttl_version += 1
            entry.expire_at = None
            self.used_memory += incoming_size
            self.lru.move_to_front(entry.lru_node)

        while self.maxmemory > 0 and self.used_memory > self.maxmemory:
            if not self._evict_lru():
                break

    def get(self, key: str) -> Optional[str]:
        if self._expire_if_needed(key):
            return None
        entry = self.store.get(key)
        if entry is None:
            return None
        self.lru.move_to_front(entry.lru_node)
        return entry.value

    def delete(self, key: str) -> int:
        self._expire_if_needed(key)
        return 1 if self._delete_key(key) else 0

    def exists(self, key: str) -> int:
        if self._expire_if_needed(key):
            return 0
        return 1 if self.store.contains(key) else 0

    def dbsize(self) -> int:
        self._purge_expired()
        return self.store.size()

    def keys(self) -> List[str]:
        self._purge_expired()
        return self.store.keys()

    def configure_maxmemory(self, value: int) -> None:
        if value < 0:
            raise ValueError("maxmemory must be >= 0")
        self.maxmemory = value

    def memory_info(self) -> Tuple[int, int, int]:
        self._purge_expired()
        return self.used_memory, self.maxmemory, self.evicted_keys

    def expire(self, key: str, seconds: int) -> int:
        if self._expire_if_needed(key):
            return 0
        entry = self.store.get(key)
        if entry is None:
            return 0
        if seconds <= 0:
            self._delete_key(key)
            return 1

        entry.ttl_version += 1
        entry.expire_at = time.time() + seconds
        self.expirations.push((entry.expire_at, entry.ttl_version, key))
        return 1

    def ttl(self, key: str) -> int:
        if self._expire_if_needed(key):
            return -2
        entry = self.store.get(key)
        if entry is None:
            return -2
        if entry.expire_at is None:
            return -1

        remaining = entry.expire_at - time.time()
        if remaining <= 0:
            self._delete_key(key)
            return -2
        return int(math.ceil(remaining))
