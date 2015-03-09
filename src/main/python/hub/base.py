
class InputNode(object):
    def read(self):
        raise NotImplementedError


class TransformationNode(object):
    def transform(self, reader):
        raise NotImplementedError


class OutputNode(object):
    def write(self, reader):
        raise NotImplementedError
