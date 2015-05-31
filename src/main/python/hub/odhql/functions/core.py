# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
from opendatahub.utils.doc import DocMixin

logger = logging.getLogger(__name__)


class OdhQLFunction(RegistrationMixin, DocMixin):
    """ Base class for all OdhQL functions. Takes care of registration and documentation generation as well as
        functionality common to all functions. A function will usually *not* directly subclass this class, but rather
        VectorizedFunction, which takes care of call semantics.
    """

    _is_abstract = True
    functions = {}
    name = ''

    def __init__(self, num_rows=1, raw_args=None):
        self.num_rows = num_rows
        self.raw_args = raw_args or []
        self.check_args()

    @staticmethod
    def gen_all_docs(section='-'):
        """
        Generated a restrucutred text by concatenating sanitizing and concatenating the docstrings of each function
        and generating a function signature.
        :param section: Symbol to use for function name headings
        :rtype unicode
        """
        doc = """
            Funktionen
            ==========

            {}
        """

        fns = OdhQLFunction.functions
        fns_help = ''.join(['{}\n'.format(fns[f].gen_doc()) for f in sorted(OdhQLFunction.functions)])
        doc = inspect.cleandoc(doc).format(fns_help)
        return doc

    @classmethod
    def gen_doc(cls, section='-'):
        """
        Generates the documentation of the current function. See gen_all_docs().
        """
        doc = super(OdhQLFunction, cls).gen_doc()
        pairs = DocMixin.get_method_args(cls.apply)[1:]  # omit self
        signature = ', '.join(['{}{}'.format(name, '=' + default if default else '') for name, default in pairs])
        title = '{}({})'.format(cls.name, signature)
        help = '{}\n{}\n{}\n'.format(title, section * len(title), doc)
        return help

    def check_args(self):
        """
        Ensures that the correct number of arguments are passed to the function.
        """
        argspec = inspect.getargspec(self.apply)
        expected_args = len(argspec.args) - (len(argspec.defaults) if argspec.defaults else 0) - 1
        given_args = len(self.raw_args)
        if given_args < expected_args:
            self.raise_error('Function takes at least {} arguments, {} given.', expected_args, given_args)

    @classmethod
    def register_child(cls, name, bases, own_dict):
        """
        See RegistrationMixin.register_child
        """
        if not own_dict.get('_is_abstract'):
            name = own_dict.get('name') or name
            cls.functions[name.lower()] = cls

    @staticmethod
    def execute(name, num_rows, args):
        fn = OdhQLFunction.create(name, num_rows, args)
        return fn.execute()

    def raise_error(self, msg, *args, **kwargs):
        """ Raise a formatted OdhQLExecutionException message
        :param msg: Error message in str.format style
        :param args: *args passed to str.format
        :param kwargs: **kwargs passed to str.format
        """
        msg = ('{}: ' + msg).format(self.name, *args, **kwargs)
        raise OdhQLExecutionException(msg)

    @contextlib.contextmanager
    def errorhandler(self, msg=None):
        """
        Context that catches any kind of exception and converts it into a formatted OdhQLExecutionException
        :param msg: Message to show instead of the original exception message.
        """
        try:
            yield
        except Exception as e:
            msg = msg.format(exception=e.message) if msg else e.message
            logger.error(traceback.format_exc())
            raise OdhQLExecutionException('{}: {}'.format(self.name, msg))

    @staticmethod
    def create(name, num_rows, args):
        try:
            cls = OdhQLFunction.functions[name.lower()]
        except KeyError:
            raise OdhQLExecutionException('Function "{}" does not exist.'.format(name))

        return cls(num_rows, args)

    def _get_single_value(self, value):
        """
        Returns the first valid (not null/none/nan) value of the series.
        """
        return value.iat[value.first_valid_index() or 0] if isinstance(value, pd.Series) else value

    def assert_in(self, name, value, possible_values):
        """
        Asserts that the parameter is one of possible_values
        """
        if value not in possible_values:
            self.raise_error('Expected parameter "{}" to be one of following: {}. Got "{}" instead.', name,
                             ', '.join(possible_values), value)

    def assert_type(self, name, value, odh_type):
        """
        Asserts that the parameter is of a certain OdhType
        """
        actual_type = OdhType.identify_value(value)
        if actual_type is not odh_type:
            self.raise_error('Expected parameter "{}" to be of type "{}". Got value "{}" of type "{}" instead.', name,
                             str(odh_type), value, str(actual_type))

    def assert_int(self, name, value):
        """
        Asserts that the parameter is an integer value or series
        """
        self.assert_type(name, self._get_single_value(value), OdhType.INTEGER)

    def assert_float(self, name, value):
        """
        Asserts that the parameter is a float value or series
        """
        self.assert_type(name, self._get_single_value(value), OdhType.FLOAT)

    def assert_value(self, name, value):
        """
        Asserts that the parameter is a singlue value/literal passed to the function and not a series/column.
        """
        if isinstance(value, pd.Series):
            self.raise_error('Expected "{}" to be a single value. Got column instead.', name)

    def assert_str(self, name, value):
        """
        Asserts that the parameter is a string value or series
        """
        self.assert_type(name, self._get_single_value(value), OdhType.TEXT)

    def assert_bool(self, name, value):
        """
        Asserts that the parameter is a boolean value or series
        """
        self.assert_type(name, self._get_single_value(value), OdhType.BOOLEAN)

    def assert_regex(self, name, value):
        """
        Asserts that the parameter is a *valid* regular expression
        """
        value = self._get_single_value(value)
        self.assert_str(name, value)
        try:
            re.compile(value)
        except sre_constants.error as e:
            self.raise_error('Invalid regular expression for parameter "{}": "{}"{}', name, e.message,
                             (not e.message.endswith('.')) * '.')

    def assert_geometry(self, name, value):
        """
        Asserts that the parameter is a geometry value or series
        """
        self.assert_type(name, self._get_single_value(value), OdhType.GEOMETRY)


class VectorizedFunction(OdhQLFunction):
    """
    Base class for all functions meant to operate on the entire series itself. E.g. CONCAT(a, b) will receive
    Series (Vectors, therefore VectoriedFunction) as parameter and consequently should return a Series of values
    (function result) again.

    It is possible that literals (single values) are passed in order to preserve memory,
    if a series is required instead, VectorizedFunction.expand can be used a helper to created a series filled with
    that value
    """
    _is_abstract = True

    def execute(self):
        return self.apply(*self.raw_args)

    def apply(self, *args):
        raise NotImplementedError

    def expand(self, arg):
        """
        :type arg: OdhSeries or any
        :return: OdhSeries if a Series was provided, otherwise a correctly shaped (size) OdhSeries filled that single
        value.
        """
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
# raise NotImplementedError
#
#
# class SampleElementFunction(ElementFunction):
# name = 'TEST'
#
# def apply(self, a, b):
# return a + b
