"""

"""


class CallbackMeta(type):
    def __init__(cls, name, bases, dct):
        cls.meta_init(name, bases, dct)
        return super(CallbackMeta, cls).__init__(name, bases, dct)


class RegistrationMixin(object):
    __metaclass__ = CallbackMeta

    @classmethod
    def meta_init(cls, name, bases, dct):
        if name != 'RegistrationMixin':
            cls.register_child(name, bases, dct)

    @classmethod
    def register_child(cls, name, bases, own_dict):
        raise NotImplementedError('Please implement when using RegistrationMixin')
