from hub.models import NodeModel
import importlib


class Pipeline(object):
    def __init__(self, model):
        super(Pipeline, self).__init__()
        self.model = model

        self.nodes = []

    def reconstruct_from_database(self):
        nodes = {}
        for model in NodeModel.objects.filter(pipeline__id=self.model.id):
            parts = model.node_class.split('.')
            module_name = '.'.join(parts[:-1])
            class_name = parts[-1]

            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)

            nodes[model.id] = cls(model)

        for node in nodes:
            if node.model.successor and nodes[node.model.successor.id]:
                node.successor = nodes[node.model.successor.id]

    def run(self):
        prev = []

        for node in self.nodes:
            if isinstance(node, InputNode):
                prev.append(node.read())
            elif isinstance(node, JoinNode):
                res = node.join(prev)
                prev = [res]
            elif isinstance(node, TransformationNode):
                prev.append(node.transform(prev.pop()))
            elif isinstance(node, OutputNode):
                node.write(prev.pop())


class Node(object):
    def __init__(self, model):
        super(Node, self).__init__()
        self.model = model

        self.params = model['params'] or {}

    def __getattr__(self, item):
        param = self.__dict__.get('params', {}).get(item)
        return param if param else super(Node, self).__getattr__(item)


class InputNode(Node):
    def __init__(self, *args, **kwargs):
        super(InputNode, self).__init__(*args, **kwargs)

    def read(self):
        raise NotImplementedError


class TransformationNode(Node):
    def __init__(self, *args, **kwargs):
        super(TransformationNode, self).__init__(*args, **kwargs)

    def transform(self, reader):
        raise NotImplementedError


class JoinNode(Node):
    def __init__(self, *args, **kwargs):
        super(JoinNode, self).__init__(*args, **kwargs)

    def join(self, readers):
        raise NotImplementedError


class OutputNode(Node):
    def __init__(self, *args, **kwargs):
        super(OutputNode, self).__init__(*args, **kwargs)

    def write(self, reader):
        raise NotImplementedError
