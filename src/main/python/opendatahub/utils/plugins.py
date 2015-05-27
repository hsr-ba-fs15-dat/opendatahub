# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib
import pkgutil


class CallbackMeta(type):
    """ Meta class for plugin loading. """
    def __init__(cls, name, bases, dct):
        cls.meta_init(name, bases, dct)
        super(CallbackMeta, cls).__init__(name, bases, dct)


class RegistrationMixin(object):
    """ Mixin for automatic plugin registration. """
    __metaclass__ = CallbackMeta

    @classmethod
    def meta_init(cls, name, bases, dct):
        """ Called once for each plugin class.
        :param name: Plugin class name
        :param bases: Plugin's base classes
        :param dct: Dict of attributes/methods of the plugin class
        :return: None
        """
        if name != 'RegistrationMixin':
            cls.register_child(name, bases, dct)

    @classmethod
    def register_child(cls, name, bases, own_dict):
        """ Registration method.
        :param name: Plugin class name
        :param bases: Plugin's base classes
        :param dct: Dict of attributes/methods of the plugin class
        :return: None
        """
        raise NotImplementedError('Please implement when using RegistrationMixin')


def import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages
    See http://stackoverflow.com/questions/3365740/how-to-import-all-submodules

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, basestring):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results
