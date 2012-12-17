import sublime

import functools


def maybe(value):
    if value is not None:
        yield value

class delayed(object):

    def __init__(self, timeout):
        self.timeout = timeout

    def __call__(self, f):

        def call_with_timeout(*args, **kwargs):
            sublime.set_timeout(functools.partial(f, *args, **kwargs),
                                self.timeout)

        return call_with_timeout
