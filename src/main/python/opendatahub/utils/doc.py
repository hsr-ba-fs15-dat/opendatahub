# -*- coding: utf-8 -*-
""" Utilities for generating documentation from inline documentation. """
from __future__ import unicode_literals

import inspect


class DocMixin(object):
    """ Mixin for generating user documentation from inline documentation. """
    UI_HELP = ''

    @classmethod
    def gen_doc(cls):
        """ Tries to find inline documentation.
        :return: Documentation, if found.
        """
        doc = inspect.cleandoc(cls.UI_HELP) or inspect.cleandoc(cls.__doc__ or '') or 'No inline documentation found'
        return doc + '\n\n'

    @staticmethod
    def get_method_args(method):
        """ Detects what arguments a method accepts.
        :param method: Method to inspect.
        :return: List of method arguments and their default values, if any.
        """
        spec = inspect.getargspec(method)
        args = spec.args
        defaults = spec.defaults or []
        defaults = [None] * (len(args) - len(defaults)) + [unicode(d) for d in defaults]
        if spec.varargs:
            args.append('...' + spec.varargs)
            defaults.append(None)

        return zip(args, defaults)
