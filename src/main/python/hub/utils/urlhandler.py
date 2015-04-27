import collections
import time

import requests as http

from opendatahub.utils.cache import cache


UrlCacheEntry = collections.namedtuple('UrlCacheEntry', ('data', 'retrieval_time'))


class UrlHelper(object):
    def fetch_url(self, url, timeout):
        cache_key = ('URL', url)
        cache_entry = cache.get(cache_key)

        if not cache_entry or cache_entry.retrieval_time < (time.time() - timeout):
            response = http.get(url)

            if response.status_code == 200:
                data = response.text.encode('utf-8')

                cache_entry = UrlCacheEntry(data, int(time.time()))
                cache.set(cache_key, cache_entry)

        if cache_entry:
            return cache_entry.data

        raise
