import collections
import time
import urlparse

import requests as http

from opendatahub.utils.cache import cache


UrlCacheEntry = collections.namedtuple('UrlCacheEntry', ('id', 'name', 'data', 'retrieval_time'))


class UrlHelper(object):
    def fetch_url(self, url_model):
        cache_key = ('URL', url_model.id)
        cache_entry = cache.get(cache_key)

        if not cache_entry or cache_entry.retrieval_time < (time.time() - url_model.refresh_after):
            response = http.get(url_model.source_url)

            _, host, path, _, _, _ = urlparse.urlparse(url_model.source_url)
            if path:
                path = path.rsplit('/', 2)[-1]
            else:
                path = host or 'url'

            if response.status_code == 200:
                data = response.text.encode('utf-8')
                cache_entry = UrlCacheEntry(url_model.id, path, data, int(time.time()))
                cache.set(cache_key, cache_entry)

        if cache_entry:
            return cache_entry.name, cache_entry.data

        raise
