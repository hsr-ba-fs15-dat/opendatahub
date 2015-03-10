import collections


class Node(object):
    nodes = collections.defaultdict(list)
    TYPE = 'undefined'

    @classmethod
    def register(cls, node_class):
        cls.nodes[node_class.TYPE].append(node_class)


class _NodeMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(_NodeMetaclass, cls).__init__(name, bases, dct)

        if 'TYPE' not in dct:
            Node.register(cls)


class InputNode(Node):
    __metaclass__ = _NodeMetaclass
    TYPE = 'input'

    @classmethod
    def accept(cls, description):
        raise NotImplementedError

    @classmethod
    def find_node_for(cls, description):
        for node in cls.nodes[cls.TYPE]:
            if node.accept and node.accept(description):
                return node()

    def read(self, description):
        raise NotImplementedError


class ParserNode(Node):
    __metaclass__ = _NodeMetaclass
    TYPE = 'parser'

    @classmethod
    def accept(cls, sample):
        raise NotImplementedError

    @classmethod
    def find_node_for(cls, sample):
        for node in cls.nodes[cls.TYPE]:
            if node.accept and node.accept(sample):
                return node()

    def parse(self, reader):
        raise NotImplementedError


class FormatterNode(Node):
    __metaclass__ = _NodeMetaclass
    TYPE = 'formatter'
    FORMAT = 'undefined'

    @classmethod
    def find_node_for(cls, format):
        for node in cls.nodes[cls.TYPE]:
            if node.FORMAT and node.FORMAT == format:
                return node()

    def format(self, reader, out):
        raise NotImplementedError


class OutputNode(Node):
    __metaclass__ = _NodeMetaclass
    TYPE = 'output'

    def write(self, reader):
        raise NotImplementedError
