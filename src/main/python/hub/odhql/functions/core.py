"""
Core/Infrastructure for OdhQL function implementations
"""

import inspect
import contextlib
import traceback
import logging

import pandas as pd
import numpy as np
import sre_constants
import re

from opendatahub.utils.plugins import RegistrationMixin
from hub.structures.frame import OdhType, OdhSeries
from ..exceptions import OdhQLExecutionException


class OdhQLFunction(RegistrationMixin):
    _is_abstract = True
    functions = {}
    name = ''

    def __init__(self, num_rows=1, raw_args=None):
        self.num_rows = num_rows
        self.raw_args = raw_args or []
        self.check_args()

    def check_args(self):
        argspec = inspect.getargspec(self.apply)
        expected_args = len(argspec.args) - (len(argspec.defaults) if argspec.defaults else 0) - 1
        given_args = len(self.raw_args)
        if given_args < expected_args:
            self.raise_error('Function takes at least {} arguments, {} given.', expected_args, given_args)

    @classmethod
    def register_child(cls, name, bases, own_dict):
        if not own_dict.get('_is_abstract'):
            name = own_dict.get('name') or name
            cls.functions[name.lower()] = cls

    @staticmethod
    def execute(name, num_rows, args):
        fn = OdhQLFunction.create(name, num_rows, args)
        return fn.execute()

    def raise_error(self, msg, *args, **kwargs):
        msg = ('{}: ' + msg).format(self.name, *args, **kwargs)
        raise OdhQLExecutionException(msg)

    @contextlib.contextmanager
    def errorhandler(self, msg=None):
        try:
            yield
        except Exception as e:
            msg = msg.format(exception=e.message) if msg else e.message
            logging.debug(traceback.format_exc())
            raise OdhQLExecutionException('{}: {}'.format(self.name, msg))

    @staticmethod
    def create(name, num_rows, args):
        try:
            cls = OdhQLFunction.functions[name.lower()]
        except KeyError:
            raise OdhQLExecutionException('Function "{}" does not exist.'.format(name))

        return cls(num_rows, args)

    def _get_single_value(self, value):
        return value.iat[value.first_valid_index() or 0] if isinstance(value, pd.Series) else value

    def assert_in(self, name, value, possible_values):
        if value not in possible_values:
            self.raise_error('Expected parameter "{}" to be one of following: {}. Got "{}" instead.', name,
                             ', '.join(possible_values), value)

    def assert_type(self, name, value, odh_type):
        actual_type = OdhType.identify_value(value)
        if actual_type is not odh_type:
            self.raise_error('Expected parameter "{}" to be of type "{}". Got value "{}" of type "{}" instead.', name,
                             str(odh_type), value, str(actual_type))

    def assert_int(self, name, value):
        self.assert_type(name, self._get_single_value(value), OdhType.INTEGER)

    def assert_float(self, name, value):
        self.assert_type(name, self._get_single_value(value), OdhType.FLOAT)

    def assert_value(self, name, value):
        if not isinstance(value, pd.Series):
            self.raise_error('Expected "{}" to be a single value. Got column instead.', name)

    def assert_str(self, name, value):
        self.assert_type(name, self._get_single_value(value), OdhType.TEXT)

    def assert_bool(self, name, value):
        self.assert_type(name, self._get_single_value(value), OdhType.BOOLEAN)

    def assert_regex(self, name, value):
        value = self._get_single_value(value)
        self.assert_str(name, value)
        try:
            re.compile(value)
        except sre_constants.error as e:
            self.raise_error('Invalid regular expression for parameter "{}": "{}"{}', name, e.message,
                             (not e.message.endswith('.')) * '.')

    def assert_geometry(self, name, value):
        self.assert_type(name, self._get_single_value(value), OdhType.GEOMETRY)


class VectorizedFunction(OdhQLFunction):
    _is_abstract = True

    def execute(self):
        return self.apply(*self.raw_args)

    def apply(self, *args):
        raise NotImplementedError

    def expand(self, arg):
        if not isinstance(arg, pd.Series):
            arg = OdhSeries(np.full(self.num_rows, arg, dtype=object if isinstance(arg, basestring) else type(arg)))

        return arg


# currently unused/not required
# class ElementFunction(OdhQLFunction):
# _is_abstract = True
#
# def execute(self):
# df = pd.DataFrame({str(i): series for i, series in enumerate(self.raw_args)})
# return df.apply(lambda s: self.apply(*s), axis=1)
#
# def apply(self, *args):
#         raise NotImplementedError
#
#
# class SampleElementFunction(ElementFunction):
#     name = 'TEST'
#
#     def apply(self, a, b):
#         return a + b
