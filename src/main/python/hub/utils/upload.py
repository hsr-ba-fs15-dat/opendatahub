# -*- coding: utf-8 -*-

"""
Utilities for upload handling.
"""

from __future__ import unicode_literals

import urlparse
import collections

import requests as http
import os
import defusedxml.ElementTree as etree

from hub.models import UrlModel, DocumentModel, FileGroupModel, FileModel
from hub.formats import Format
from hub.structures.file import File


class UploadHandler(object):
    """ Utility class for upload handling. """

    def handle_upload(self, request):
        """
        Creates a document from the django request.
        :param request: django request
        :return: the new document.
        """
        doc = DocumentModel(name=request.data['name'], description=request.data['description'],
                            private=request.data.get('private', False), owner=request.user)
        doc.save()

        if 'url' in request.data:
            file_groups = UrlHandler().handle_url_upload(request, doc)

        elif 'file' in request.data:
            file_groups = FileHandler().handle_file_upload(request, doc)

        else:
            raise RuntimeError('No data source specified')

        for fg in file_groups:
            # enforce that everything must be parseable and is cached
            fg.to_file_group().to_df()

        return doc


class FileHandler(object):
    """ Utility class for file uploads. """

    def handle_file_upload(self, request, document):
        """
        Creates files/file groups from the django request.
        :param request: django request
        :param document: document to add files/file groups to.
        :return: the newly created file groups.
        """
        files = request.data.getlist('file')
        format_name = request.data.get('format')
        specified_format = Format.from_string(format_name) if format_name else None

        groups = collections.defaultdict(list)

        for file in files:
            name = os.path.splitext(file.name)[0]
            groups[name].append(file)

        file_groups = []
        for group in groups.itervalues():
            file_group = FileGroupModel(document=document)
            file_group.save()
            file_groups.append(file_group)

            for file in group:
                file = File.from_string(file.name, file.read())
                concrete_format = specified_format or Format.identify(file)

                file_model = FileModel(file_name=file.name, data=file.stream.read(), file_group=file_group,
                                       format=concrete_format.name)
                file_model.save()

        return file_groups


class UrlHandler(object):
    """ Utility class for url-based uploads. """

    def handle_url_upload(self, request, doc):
        """
        Creates url models/file groups from the django request.
        :param request: django request
        :param doc: document to add url models/file groups to.
        :return: the newly created file groups
        """
        url = request.data.get('url').strip()

        try:
            refresh = int(request.data.get('refresh'))
        except:
            refresh = 3600

        if refresh < 60:
            refresh = 60
        if refresh > 86400:
            refresh = 86400

        is_wfs = self.check_wfs(url)
        type = 'wfs' if is_wfs else 'auto'
        specified_format = request.data.get('format')

        file_group = FileGroupModel(document=doc)
        file_group.save()

        url_model = UrlModel(source_url=url, refresh_after=refresh, type=type, file_group=file_group,
                             format=specified_format)
        url_model.save()

        return [file_group]

    def check_wfs(self, url):
        """
        Checks if the given url looks like a WFS service endpoint.
        For more information on WFS, see http://www.opengeospatial.org/standards/wfs
        :param url: http(s) url to check.
        :return: True if the url looks like a WFS endpoint, False otherwise.
        """
        (scheme, host, path, _, _, _) = urlparse.urlparse(url)

        query = {'request': 'GetCapabilities', 'service': 'wfs'}
        query_string = '&'.join(['{}={}'.format(k, v) for k, v in query.items()])

        capabilities_url = '{}://{}/{}?{}'.format(scheme, host, path, query_string)

        try:
            capabilities_request = http.get(capabilities_url, headers={'Accept': 'text/xml'})

            if capabilities_request.status_code != 200:
                return False

            wfs_xml = etree.fromstring(capabilities_request.text.encode('utf-8'))

            namespaces = {'ows': 'http://www.opengis.net/ows'}

            ident = wfs_xml.find('ows:ServiceIdentification', namespaces)
            if ident is not None:
                return True
        except:
            pass

        return False
