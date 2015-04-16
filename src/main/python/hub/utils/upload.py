import requests as http
import urlparse

import defusedxml.ElementTree as etree
import collections

from  hub.models import UrlModel, DocumentModel, FileGroupModel, FileModel


class UploadHandler(object):
    def handleUpload(self, request):

        doc = DocumentModel(name=request.data['name'], description=request.data['description'],
                            private=request.data.get('private', False), owner=request.user)
        doc.save()

        if 'url' in request.data:
            UrlHandler().handleUrlUpload(request, doc)

        elif 'file' in request.data:
            FileHandler().handleFileUpload(request, doc)

        else:
            raise RuntimeError('No data source specified')

        return doc


class FileHandler(object):

    def handleFileUpload(self, request, document):
        files = request.data.getlist('file')

        groups = collections.defaultdict(list)

        for file in files:
            name = os.path.splitext(file.name)[0]
            groups[name].append(file)

        for group in groups.itervalues():
            file_group = FileGroupModel(document=document, format=request.data.get('format', None))
            file_group.save()

            for file in group:
                file_model = FileModel(file_name=file.name, data=file.read(), file_group=file_group)
                file_model.save()


class UrlHandler(object):

    def handleUrlUpload(self, params, doc):

        url = params['url']

        is_wfs = self.checkWfs(url)
        type = 'wfs' if is_wfs else 'auto'

        url_model = UrlModel(source_url=url, type=type, document=doc)
        url_model.save()

    def checkWfs(self, url):
        (scheme, host, path, _, _, _) = urlparse.urlparse(url)

        query = {'request': 'GetCapabilities', 'service': 'wfs'}
        query_string = '&'.join(['{}={}'.format(k,v) for k,v in query.items()])

        capabilities_url = '{}://{}/{}?{}'.format(scheme, host, path, query_string)

        capabilities_request = http.get(capabilities_url, headers={'Accept', 'text/xml'})

        if capabilities_request.status_code != 200:
            return False

        try:
            wfs_xml = etree.fromstring(capabilities_request.text.encode('utf-8'))

            namespaces = {'ows':'http://www.opengis.net/ows'}

            ident = wfs_xml.find('ows:ServiceIdentification', namespaces)
            if ident:
                return True
        except:
            pass

        return False
