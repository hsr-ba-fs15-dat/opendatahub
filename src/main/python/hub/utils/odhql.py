# -*- coding: utf-8 -*-

""" Utilities for ODHQL query handling """

from __future__ import unicode_literals

import itertools
import logging

from django.db.models import Q
from django.utils.text import slugify

from django.db import connection, DatabaseError

from hub.odhql.interpreter import OdhQLInterpreter
from hub.odhql.exceptions import OdhQLExecutionException
from hub.models import FileGroupModel, TransformationModel
from opendatahub.utils import cache
from opendatahub import settings


class TransformationUtil(object):
    """Helper class for transformation handling."""

    @staticmethod
    def interpret(query, user_id=None):
        """
        Execute a given query: Fetch required data sources, check permissions, and finally interpret the statement.
        :param query: The query to run.
        :param user_id: Optional user id to check for. Note: If None, only public data source are available.
        :return: Resulting data frame.
        """
        file_group_ids, transformation_ids = OdhQLInterpreter.parse_sources(query)

        permission_filter = (Q(document__private=False) | Q(document__owner=user_id)
                             if user_id else Q(document__private=False))
        fgs = FileGroupModel.objects.filter(Q(id__in=file_group_ids.values()) & permission_filter)

        file_group_pairs = [(fg.id, df) for fg in fgs for df in fg.to_file_group().to_df()]
        transformation_pairs = [(id, TransformationUtil.df_for_transformation(id)) for id in
                                transformation_ids.values()]

        sources = {'odh{}_{}'.format(id, df.name.lower()): df for id, df in file_group_pairs}

        # allows for lookup without name -> ODH5 (takes the first df if more than one is present)
        sources.update({'odh{}'.format(id): df for id, df in reversed(file_group_pairs)})

        sources.update({'trf{}'.format(id): df for id, df in reversed(transformation_pairs)})

        # limit sources to ones actually referenced in the query
        sources = {name: sources[name]
                   for name in itertools.chain(file_group_ids.keys(), transformation_ids.keys())
                   if name in sources}

        df = OdhQLInterpreter(sources).execute(query)

        return df

    @staticmethod
    def df_for_transformation(tf, user_id=None):
        """
        Fetches the data frame for a given transformation.
        :param tf: Transformation model instance or id.
        :param user_id: Optional user id to check for. Note: If None, only public data sources are available.
        :return: Resulting data frame.
        """
        if isinstance(tf, TransformationModel):
            id = tf.id
            model = tf
        else:
            id = tf
            model = None

        cache_key = ('TRF', id)
        df = cache.get(cache_key)

        if df is None:
            if model is None:
                model = TransformationModel.objects.get(id=id)
                if model.private and (not user_id or model.owner != user_id):
                    raise OdhQLExecutionException('Fehlende Berechtigung')
            df = TransformationUtil.interpret(model.transformation)
            df.name = slugify(unicode(model.name))

            cache.set(cache_key, df)

        return df

    @staticmethod
    def invalidate_related_cache(file_groups=set(), transformations=set()):
        """ Fetches all related transformations for both file groups and transformations, in order to remove them from
        the cache. This uses a recursive CTE in PostgreSQL syntax.

        The statement might look like this;

        with recursive related(id) as (
          values (2005), (2001)
           union
          select g.transformationmodel_id
            from hub_transformationmodel_referenced_file_groups g
          where g.filegroupmodel_id in (8)
           union
          select t.from_transformationmodel_id
            from hub_transformationmodel_referenced_transformations t
            join related r on t.to_transformationmodel_id = r.id )
         select id
           from related;

        :param file_groups: Set of ids
        :param transformations: Set of ids
        :return: None
        """

        parts = ['with recursive related(id) as (']

        if not len(file_groups) and not len(transformations):
            return

        if len(file_groups):
            parts.append('select g.transformationmodel_id from hub_transformationmodel_referenced_file_groups g '
                         'where g.filegroupmodel_id in ({}) union '.format(', '.join([str(id) for id in file_groups])))

        if len(transformations):
            parts.append('values ')
            parts.append(', '.join(['({})'.format(id) for id in transformations]))
            parts.append(' union ')

        parts.append('select t.from_transformationmodel_id from hub_transformationmodel_referenced_transformations t '
                     'join related r on t.to_transformationmodel_id = r.id ) select id from related')

        with connection.cursor() as cursor:
            try:
                cursor.execute(''.join(parts))

                for (id,) in cursor.fetchall():
                    cache.delete((settings.TRANSFORMATION_PREFIX, id))

                cursor.close()
            except DatabaseError:
                logging.error('Failed to read related transformations from database - raw query may be written for '
                              'different database')
