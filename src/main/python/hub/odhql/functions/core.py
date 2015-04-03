"""

"""

import inspect

import pandas as pd

from opendatahub.utils.plugins import RegistrationMixin
from ..exceptions import OdhQLExecutionException


class OdhQLFunction(RegistrationMixin):
    _is_abstract = True
    functions = {}

    name = ''

    def __init__(self, raw_args=None):
        self.raw_args = raw_args or []
        self.check_args()

    def check_args(self):
        argspec = inspect.getargspec(self.apply)
        expected_args = len(argspec.args) - 1
        given_args = len(self.raw_args)
        if not (argspec.keywords or argspec.varargs) and given_args != expected_args:
            raise OdhQLExecutionException(
                '{} takes exactly {} arguments, {} given'.format(self.name, expected_args, given_args))

    @classmethod
    def register_child(cls, name, bases, own_dict):
        if not own_dict.get('_is_abstract'):
            name = own_dict.get('name') or name
            cls.functions[name.lower()] = cls

    @staticmethod
    def execute(name, args):
        fn = OdhQLFunction.create(name, args)
        return fn.execute()

    @staticmethod
    def create(name, args):
        try:
            cls = OdhQLFunction.functions[name.lower()]
        except KeyError:
            raise OdhQLExecutionException('Function "{}" does not exist'.format(name))

        return cls(args)


class VectorizedFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        df = pd.DataFrame({str(i): series for i, series in enumerate(self.raw_args)})
        return self.apply(*[df[c] for c in df.columns])

    def apply(self, *args):
        raise NotImplementedError


class ElementFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        df = pd.DataFrame({str(i): series for i, series in enumerate(self.raw_args)})
        return df.apply(lambda s: self.apply(*s), axis=1)

    def apply(self, *args):
        raise NotImplementedError


class SampleElementFunction(ElementFunction):
    name = 'TEST'

    def apply(self, a, b):
        return a + b
