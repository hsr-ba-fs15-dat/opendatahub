# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
"""

import inspect


class DocMixin(object):
    UI_HELP = ''

    @classmethod
    def gen_doc(cls):
        doc = inspect.cleandoc(cls.UI_HELP) or inspect.cleandoc(cls.__doc__ or '') or 'No inline documentation found'
        return doc + '\n\n'

    @staticmethod
    def get_method_args(method):
        spec = inspect.getargspec(method)
        args = spec.args
        defaults = spec.defaults or []
        defaults = [None] * (len(args) - len(defaults)) + [unicode(d) for d in defaults]
        if spec.varargs:
            args.append('...' + spec.varargs)
            defaults.append(None)

        return zip(args, defaults)
