# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Copy of django local memory cache but without pickling overhead
"""

"Thread-safe in-memory cache backend."

import time

from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT
from django.utils.synch import RWLock


# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches = {}
_expire_info = {}
_locks = {}


class LocMemNoPickleCache(BaseCache):
    def __init__(self, name, params):
        BaseCache.__init__(self, params)
        self._cache = _caches.setdefault(name, {})
        self._expire_info = _expire_info.setdefault(name, {})
        self._lock = _locks.setdefault(name, RWLock())

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.writer():
            if self._has_expired(key):
                self._set(key, value, timeout)
                return True
            return False

    def get(self, key, default=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        value = None
        with self._lock.reader():
            if not self._has_expired(key):
                value = self._cache[key]
        if value is not None:
            return value
        with self._lock.writer():
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT):
        if len(self._cache) >= self._max_entries:
            self._cull()
        self._cache[key] = value
        self._expire_info[key] = self.get_backend_timeout(timeout)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.writer():
            self._set(key, value, timeout)

    def incr(self, key, delta=1, version=None):
        value = self.get(key, version=version)
        if value is None:
            raise ValueError("Key '%s' not found" % key)
        new_value = value + delta
        key = self.make_key(key, version=version)
        with self._lock.writer():
            self._cache[key] = new_value
        return new_value

    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.reader():
            if not self._has_expired(key):
                return True

        with self._lock.writer():
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False

    def _has_expired(self, key):
        exp = self._expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache) if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock.writer():
            self._delete(key)

    def clear(self):
        self._cache.clear()
        self._expire_info.clear()


# For backwards compatibility
class CacheClass(LocMemNoPickleCache):
    pass
