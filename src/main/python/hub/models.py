from django.db import models
from picklefield.fields import PickledObjectField


class PipelineModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=2000)


class NodeModel(models.Model):
    pipeline = models.ForeignKey(PipelineModel, null=False)
    successor = models.ForeignKey('NodeModel', null=True)

    params = PickledObjectField()

    # this probably needs to be a relation of it's own for ui reasons (need to know which fields are applicable, etc.)
    node_class = models.CharField(max_length=200, null=False)
