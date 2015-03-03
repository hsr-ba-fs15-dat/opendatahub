from django.db import models
from picklefield.fields import PickledObjectField

import csv


class Pipeline(models.Model):
    name = models.CharField()
    description = models.TextField()

    def __init__(self, name, description, nodes):
        super(Pipeline, self).__init__(name=name, description=description)
        self.nodes = nodes

    def run(self):
        prev = []

        for node in self.nodes:
            if isinstance(node, InputNode):
                prev.append(node.read())
            elif isinstance(node, JoinNode):
                res = node.merge(prev)
                prev = [res]
            elif isinstance(node, TransformationNode):
                prev.append(node.transform(prev.pop()))
            elif isinstance(node, OutputNode):
                node.write(prev.pop())


class Node(models.Model):

    successor = models.OneToOneField('self', null=True)
    params = PickledObjectField()

    class Meta:
        abstract = True

    def __init__(self, **params):
        super(Node, self).__init__(successor=None)  # TODO
        self.params = params

    def __getattr__(self, item):
        param = self.__dict__.get('params', {}).get(item)
        return param if param else super(Node, self).__getattr__(item)


class InputNode(Node):
    pipeline = models.OneToOneField(Pipeline)

    def read(self):
        raise NotImplementedError


class OutputNode(Node):
    def write(self, reader):
        raise NotImplementedError


class TransformationNode(Node):
    def transform(self, reader):
        raise NotImplementedError


class JoinNode(Node):
    def merge(self, readers):
        raise NotImplementedError


class FileInputNode(InputNode):
    def __init__(self, filename):
        super(FileInputNode, self).__init__(filename=filename)

    def read(self):
        with open(self.filename, 'r') as file_input:
            for line in file_input:
                yield line


class CsvInput(TransformationNode):
    def __init__(self):
        super(CsvInput, self).__init__()

    def transform(self, reader):
        csv_reader = csv.DictReader(reader)
        for row in csv_reader:
            yield row


class SequentialMerger(JoinNode):
    def __init__(self):
        super(SequentialMerger, self).__init__()

    def merge(self, readers):
        for reader in readers:
            for row in reader:
                yield row


class NormalizedAddressToGarbageTransform(TransformationNode):
    def __init__(self):
        super(NormalizedAddressToGarbageTransform, self).__init__()

    def transform(self, reader):
        for row in reader:
            converted = {
                'Name': '{} {}'.format(row['Name'], row['Surname']),
                'Street': '{} {}'.format(row['Street'], row['No']),
                'City': '{} {}'.format(row['Zip'], row['City'])
            }
            yield converted


class CsvOutputNode(OutputNode):
    def __init__(self, filename, field_names):
        super(CsvOutputNode, self).__init__(filename=filename, field_names=field_names)

    def write(self, reader):
        with open(self.filename, 'w') as output:
            csv_writer = csv.DictWriter(output, self.field_names)
            csv_writer.writeheader()

            for row in reader:
                csv_writer.writerow(row)
