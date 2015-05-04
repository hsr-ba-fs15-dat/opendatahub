import itertools

from hub.odhql.interpreter import OdhQLInterpreter
from hub.models import FileGroupModel, TransformationModel
from opendatahub.utils import cache
from django.utils.text import slugify


class TransformationUtil(object):
    @staticmethod
    def interpret(query):
        file_group_ids, transformation_ids = OdhQLInterpreter.parse_sources(query)

        fgs = FileGroupModel.objects.filter(id__in=file_group_ids.values())

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
    def df_for_transformation(tf):
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
            df = TransformationUtil.interpret(model.transformation)
            df.name = slugify(unicode(tf.name))

            cache.set(cache_key, df)

        return df
