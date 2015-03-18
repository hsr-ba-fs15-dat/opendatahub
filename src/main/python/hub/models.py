import base64

from django.db import models


def cap(str, length):
    return str if len(str) < length else str[0:length - 3] + '...'


class DocumentModel(models.Model):
    class Meta:
        db_table = 'hub_documents'

    name = models.CharField(max_length=200)
    description = models.TextField()

    private = models.BooleanField(default=False)

    _content = models.TextField(db_column='content', blank=True)

    def set_content(self, data):
        self._content = base64.encodestring(data)

    def get_content(self):
        return base64.decodestring(self._content)

    content = property(get_content, set_content)

    def __str__(self):
        return "[Document id={} description={}]".format(self.id, cap(self.description, 50))

