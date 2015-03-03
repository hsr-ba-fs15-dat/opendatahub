# from django.db import models

# Create your models here.


class Node(object):
    def __init__(self, name=None, parameters=None):
        """
        :type name: str
        :type parameters: dict
        """
        self.name = name or self.__class__.__name__
        self.parameters = parameters or {}


class Input(Node):
    def __init__(self, name=None, parameters=None):
        super(Input, self).__init__(name, parameters)

    def read(self):
        pass


class Output(Node):
    def __init__(self, name=None, parameters=None):
        super(Output, self).__init__(name, parameters)

    def write(self, reader):
        pass


class Transformation(Node):
    def __init__(self, name=None, parameters=None):
        super(Transformation, self).__init__(name, parameters)

    def transform(self, reader):
        pass


class Merge(Node):
    def __init__(self, name=None, parameters=None):
        super(Merge, self).__init__(name, parameters)

    def merge(self, readers):
        pass


class Pipeline(object):
    def __init__(self, name, description, nodes):
        self.name = name
        self.description = description
        self.nodes = nodes

    def run(self):
        prev = None

        for node in self.nodes:
            if isinstance(node, Input):
                prev = node.read()
            elif isinstance(node, Transformation):
                prev = node.transform(prev)
            elif isinstance(node, Output):
                node.write(prev)
