from threading import Thread

from django.core.cache import cache as default_cache, caches
from django.db import connections, router
import types


class CacheWrapper(object):
    def __init__(self, django_cache):
        self._cache = django_cache

    @classmethod
    def make_key(cls, key):
        if isinstance(key, (basestring, int, float)):
            key = str(key)
        elif isinstance(key, (types.ListType, types.TupleType)):
            key = ':'.join([str(part) for part in key])
        else:
            key = hash(key)
        return key

    def set(self, key, value, version=None):
        self._cache.set(self.make_key(key), value, version=version)

    def get(self, key, version=None):
        return self._cache.get(self.make_key(key), version=version)

    def delete(self, key, cascade=False, version=None):
        self._cache.delete(key, version=version)


class LocalCacheWrapper(CacheWrapper):
    def delete(self, key, version=None, cascade=True):
        key = self._cache.make_key(self.make_key(key))
        if cascade:
            keys = [k.startswith(key) for k in self._cache._cache.iterkeys()]
            self._cache.delete_many(keys)
        else:
            super(LocalCacheWrapper, self).delete(key, version=version)


class DatabaseCacheWrapper(CacheWrapper):
    def set(self, key, value, **kw):
        # fire and forget
        Thread(target=super(DatabaseCacheWrapper, self).set, args=(key, value), kwargs=kw).start()

    def delete(self, key, version=None, cascade=True):
        key = self._cache.make_key(self.make_key(key))
        if cascade:
            db = router.db_for_write(self._cache.cache_model_class)
            table = connections[db].ops.quote_name(self._cache._table)
            with connections[db].cursor() as cursor:
                cursor.execute("DELETE FROM %s WHERE cache_key LIKE %%s" % table, [key + '%'])
        else:
            super(DatabaseCacheWrapper, self).delete(key, version=version)


L1 = LocalCacheWrapper(caches['L1'])
L2 = LocalCacheWrapper(default_cache)
L3 = DatabaseCacheWrapper(caches['L3'])


def set(key, value, l1=False, l2=True, l3=True, version=None):
    for cache in [c for c, do in ((L1, l1), (L2, l2), (L3, l2)) if do]:
        cache.set(key, value, version=version)


def get(key, l1=False, l2=True, l3=True, version=None):
    for cache in [c for c, do in ((L1, l1), (L2, l2), (L3, l2)) if do]:
        value = cache.get(key, version=version)
        if value is not None:
            return value


def delete(key, l1=True, l2=True, l3=True, version=None, cascade=True):
    for cache in [c for c, do in ((L1, l1), (L2, l2), (L3, l2)) if do]:
        cache.delete(key, cascade=True, version=version)
