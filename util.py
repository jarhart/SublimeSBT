import sublime

import functools
import itertools
import threading


def maybe(value):
    if value is not None:
        yield value


def group_by(xs, kf):
    grouped = {}
    for k, i in itertools.groupby(xs, kf):
        grouped.setdefault(k, []).extend(i)
    return grouped


class delayed(object):

    def __init__(self, timeout):
        self.timeout = timeout

    def __call__(self, f):

        def call_with_timeout(*args, **kwargs):
            sublime.set_timeout(functools.partial(f, *args, **kwargs),
                                self.timeout)

        return call_with_timeout


class SynchronizedCache(object):

    def __init__(self):
        self.__items = {}
        self.__lock = threading.RLock()

    def __call__(self, key, f):
        with self.__lock:
            if key not in self.__items:
                self.__items[key] = f()
            return self.__items[key]


class MetaOnePerWindow(type):

    def __init__(cls, name, bases, dct):
        super(MetaOnePerWindow, cls).__init__(name, bases, dct)
        cls.instance_cache = SynchronizedCache()

    def __call__(cls, window):
        return cls.instance_cache(window.id(), lambda: type.__call__(cls, window))


OnePerWindow = MetaOnePerWindow('OnePerWindow', (object,), {})
