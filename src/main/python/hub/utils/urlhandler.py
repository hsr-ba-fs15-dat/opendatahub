from opendatahub.utils.cache import cache
import collections
import time

import requests as http


UrlCacheEntry = collections.namedtuple('UrlCacheEntry', ('id', 'data', 'retrieval_time'))

class UrlHelper(object):

    def fetchUrl(self, url_model):
        cache_key = ('URL', url_model.id)
        cache_entry = cache.get(cache_key)

        if not cache_entry or cache_entry.retrieval_time < (time.time() - url_model.refresh_after):
            response = http.get(url_model.source_url)

            if response.status_code == 200:
                data = response.text.encode('utf-8')
                cache_entry = UrlCacheEntry(url_model.id, data, int(time.time()))
                cache.set(cache_key, cache_entry)

        if cache_entry:
            return cache_entry.data

        raise
