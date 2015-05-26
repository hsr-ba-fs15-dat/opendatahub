# -*- coding: utf-8 -*-

""" Utilities for ODHQL query handling """

from __future__ import unicode_literals

import itertools

from django.db.models import Q
from django.utils.text import slugify

from hub.odhql.interpreter import OdhQLInterpreter
from hub.odhql.exceptions import OdhQLExecutionException
from hub.models import FileGroupModel, TransformationModel
from opendatahub.utils import cache


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
