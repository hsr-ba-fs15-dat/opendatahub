import collections

known_formatters = collections.OrderedDict()


class FormatterDescription(object):
    def __init__(self, name, description, mime_type='text/plain', file_extension='txt'):
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.file_extension = file_extension


class FormatterBase(object):
    description = None

    @classmethod
    def register(cls, node_class):
        if node_class.description and node_class.description is not None:
            known_formatters[node_class.description.name] = node_class


class FormatAlreadyRegisteredError(RuntimeError):
    pass


class _FormatterMetaclass(type):
    def __init__(cls, name, bases, dct):
        super(_FormatterMetaclass, cls).__init__(name, bases, dct)

        if 'TYPE' not in dct:
            FormatterBase.register(cls)


class Formatter(FormatterBase):
    __metaclass__ = _FormatterMetaclass

    def format(self, document, writer, parameters):
        raise NotImplementedError
