import glob

import os


modules = glob.glob(os.path.dirname(__file__) + '/*.py')
__all__ = [os.path.basename(f)[:-3] for f in modules if not f.endswith('__init__.py')]
map(__import__, map(lambda x: 'hub.formatters.' + x, __all__))

from .base import Formatter, CSVFormatter, OGRFormatter  # noqa

format = Formatter.format
