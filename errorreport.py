try:
    from .sbterror import SbtError
    from .util import maybe
except(ValueError):
    from sbterror import SbtError
    from util import maybe


class ErrorReport(object):

    def __init__(self):
        self._errors = {}
        self._old_errors = {}
        self._new_errors = {}
        self._set_current(None)

    def clear(self):
        self._errors.clear()
        self._old_errors.clear()
        self._new_errors.clear()
        self._set_current(None)

    def add_error(self, error):
        if error.filename not in self._new_errors:
            self._new_errors[error.filename] = {}
        file_errors = self._new_errors[error.filename]
        if error.line not in file_errors:
            file_errors[error.line] = []
        file_errors[error.line].append(error)
        self._merge_errors()

    def cycle(self):
        self._old_errors = self._new_errors
        self._new_errors = {}
        self._merge_errors()

    def all_errors(self):
        for filename in sorted(self._errors.keys()):
            for error in self.sorted_errors_in(filename):
                yield error

    def focus_error(self, error):
        for i, e in enumerate(self.all_errors()):
            if e == error:
                self._set_current(i)

    def next_error(self):
        sorted_errors = list(self.all_errors())
        if sorted_errors:
            if self._index is None:
                self._set_current(0)
            else:
                self._set_current((self._index + 1) % len(sorted_errors))
        else:
            self._set_current(None)
        return self.current_error

    def sorted_errors_in(self, filename):

        def sort_errors(errors):
            for line in sorted(errors.keys()):
                for error in sorted(errors[line], key=lambda e: e.error_type):
                    yield error

        for errors in maybe(self.errors_in(filename)):
            return list(sort_errors(errors))

    def errors_at(self, filename, line):
        for errors in maybe(self.errors_in(filename)):
            return errors.get(line)

    def errors_in(self, filename):
        return self._errors.get(filename)

    def current_error_in(self, filename):
        for error in maybe(self.current_error):
            if error.filename == filename:
                return error

    def clear_file(self, filename):
        for errors in [self._old_errors, self._new_errors, self._errors]:
            if filename in errors:
                del errors[filename]
        if self.current_error_in(filename):
            self._set_current(None)

    def has_errors(self):
        return len(self._errors) > 0

    def _merge_errors(self):
        self._errors = dict(list(self._old_errors.items()) + list(self._new_errors.items()))
        self._set_current(None)

    def _set_current(self, i):
        sorted_errors = list(self.all_errors())
        if i is not None and i < len(sorted_errors):
            self._index = i
            self.current_error = sorted_errors[i]
        else:
            self._index = None
            self.current_error = None
