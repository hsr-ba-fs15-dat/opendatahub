
import os

from django.test import TestCase
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opendatahub.settings')
django.setup()

base_dir = os.path.abspath(os.path.dirname(__file__))


class PipelineSetupTest(TestCase):
    def setUp(self):

        from hub import models
        pipeline = models.PipelineModel(name='TestPipeline', description='Example pipeline to test the api',)
        pipeline.save()

        csv_out = models.NodeModel(pipeline=pipeline,
                                   node_class='hub.nodes.CsvOutput',
                                   params={
                                       'filename': os.path.join(base_dir, 'test-addresses-out.csv'),
                                       'fields': ('Name', 'Street', 'City')
                                   })
        csv_out.save()

        transform = models.NodeModel(pipeline=pipeline,
                                     node_class='hub.nodes.NormalizedAddressToGarbageTransform',
                                     successor=csv_out)
        transform.save()

        merger = models.NodeModel(pipeline=pipeline, node_class='hub.nodes.SequentialJoin', successor=transform)
        merger.save()

        csv_in = models.NodeModel(pipeline=pipeline, node_class='hub.nodes.CsvInput', successor=merger)
        csv_in.save()
        file_in = models.NodeModel(pipeline=pipeline, node_class='hub.nodes.FileInput',
                                   params={'filename':  os.path.join(base_dir, 'test-addresses.csv')},
                                   successor=csv_in)
        file_in.save()

        csv_in_2 = models.NodeModel(pipeline=pipeline, node_class='hub.nodes.CsvInput', successor=merger)
        csv_in_2.save()
        file_in_2 = models.NodeModel(pipeline=pipeline, node_class='hub.nodes.FileInput',
                                     params={'filename':  os.path.join(base_dir, 'test-addresses2.csv')},
                                     successor=csv_in_2)
        file_in_2.save()

    def runTest(self):
        pass