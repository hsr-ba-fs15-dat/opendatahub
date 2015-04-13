"""

"""

import inspect

import pandas as pd
import numpy as np
import sre_constants
import re

from opendatahub.utils.plugins import RegistrationMixin
from ..exceptions import OdhQLExecutionException


class OdhQLFunction(RegistrationMixin):
    _is_abstract = True
    functions = {}

    name = ''

    _type_assertions = {
        'integer': int,
        'string': basestring,
        'float': float,
        'boolean': bool,
    }

    def __init__(self, num_rows=1, raw_args=None):
        self.num_rows = num_rows
        self.raw_args = raw_args or []
        self.check_args()

    def check_args(self):
        argspec = inspect.getargspec(self.apply)
        expected_args = len(argspec.args) - 1
        given_args = len(self.raw_args)
        if not (argspec.keywords or argspec.varargs) and given_args != expected_args:
            raise OdhQLExecutionException(
                '{} takes exactly {} arguments, {} given.'.format(self.name, expected_args, given_args))

    @classmethod
    def register_child(cls, name, bases, own_dict):
        if not own_dict.get('_is_abstract'):
            name = own_dict.get('name') or name
            cls.functions[name.lower()] = cls

    @staticmethod
    def execute(name, num_rows, args):
        fn = OdhQLFunction.create(name, num_rows, args)
        return fn.execute()

    @staticmethod
    def create(name, num_rows, args):
        try:
            cls = OdhQLFunction.functions[name.lower()]
        except KeyError:
            raise OdhQLExecutionException('Function "{}" does not exist.'.format(name))

        return cls(num_rows, args)

    def assert_in(self, name, value, possible_values):
        if value not in possible_values:
            raise OdhQLExecutionException('Expected parameter "{}" of function "{}" to be one of following: {}. '
                                          'Got "{}" instead.'.format(name, self.name, ', '.join(possible_values),
                                                                     value))

    def assert_type(self, name, value, type_name):
        type_ = self._type_assertions[type_name]
        if not isinstance(value, type_):
            raise OdhQLExecutionException('Expected parameter "{}" of function "{}" to be of type "{}". '
                                          'Got value "{}" of type "{}" instead.'.format(name, self.name, type_name,
                                                                                        value,
                                                                                        type(value).__name__))

    def assert_int(self, name, value):
        self.assert_type(name, value, 'integer')

    def assert_str(self, name, value):
        self.assert_type(name, value, 'string')

    def assert_bool(self, name, value):
        self.assert_type(name, value, 'boolean')

    def assert_regex(self, name, value):
        self.assert_str(name, value)
        try:
            re.compile(value)
        except sre_constants.error as e:
            raise OdhQLExecutionException('Invalid regular expression for parameter "{}" of function "{}": "{}"'
                                          .format(name, self.name, e.message))


class VectorizedFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        return self.apply(*self.raw_args)

    def apply(self, *args):
        raise NotImplementedError

    def expand(self, arg):
        if not isinstance(arg, pd.Series):
            arg = pd.Series(np.full(self.num_rows, arg, dtype=object if isinstance(arg, basestring) else type(arg)))

        return arg


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