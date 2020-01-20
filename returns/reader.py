# -*- coding: utf-8 -*-

from returns.primitives.container import BaseContainer


class Reader(BaseContainer):
    def __init__(self, function_or_value):
        if callable(function_or_value):
            func = function_or_value
        else:
            func = lambda _: function_or_value

        super(Reader, self).__init__(func)

    def __call__(self, *args):
        value = self.__getstate__()
        args_count = len(args)
        for arg in args:
            try:
                value = value(arg)
            except TypeError:
                raise TypeError('Too many arguments!')

        if callable(value):
            return Reader(value)
        else:
            return value

    def _mul_(self, func):
        return func.fmap(self)

    def fmap(self, a_function):
        return Reader(lambda x: a_function(self.__getstate__()(x)))

    def amap(self, functor_value):
        return Reader(lambda x: self(x)(functor_value(x)))

    def bind(self, function):
        return Reader(lambda x: function(self.__getstate__()(x))(x))

    @classmethod
    def unit(cls, value):
        return Reader(lambda _: value)
