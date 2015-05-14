# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .core import *  # noqa

from opendatahub.utils.plugins import import_submodules
import plugins


# import everything into this module for backward compatibility (loadfixtures, etc.)
for name, module in import_submodules('hub.formats').iteritems():
    self = globals()
    for key in (k for k in dir(module) if not k.startswith('__')):
        self[key] = module.__dict__[key]

import_submodules(plugins)


identify = Format.identify
format = Formatter.format
parse = Parser.parse
