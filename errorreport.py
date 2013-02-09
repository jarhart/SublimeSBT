try:
    from .util import maybe
except(ValueError):
    from util import maybe


class SbtError(object):

    def __init__(self, filename, line, message, error_type='error'):
        self.filename = filename
        self.line = int(line)
        self.message = message
        self.error_type = error_type

    def list_item(self, relative_path):
        path = relative_path(self.filename)
        return [self.message, '%s:%i' % (path, self.line)]

    def encoded_position(self):
        return '%s:%i' % (self.filename, self.line)


class ErrorReport(object):

    def __init__(self):
        self._errors = {}
        self._old_errors = {}
        self._new_errors = {}

    def clear(self):
        self._errors.clear()
        self._old_errors.clear()
        self._new_errors.clear()

    def add_error(self, filename, line, message, error_type='error'):
        error = SbtError(filename, line, message, error_type)
        if filename not in self._new_errors:
            self._new_errors[filename] = {}
        file_errors = self._new_errors[filename]
        if error.line not in file_errors:
            file_errors[error.line] = []
        file_errors[error.line].append(error)
        self._merge_errors()
        return error

    def cycle(self):
        self._old_errors = self._new_errors
        self._new_errors = {}
        self._merge_errors()

    def all_errors(self):
        for filename in sorted(self._errors.keys()):
            for line in sorted(self._errors[filename].keys()):
                for error in self._errors[filename][line]:
                    yield error

    def sorted_errors_in(self, filename):

        def sort_errors(errors):
            for line in sorted(errors.keys()):
                for error in sorted(errors[line], key=lambda e: e.error_type):
                    yield error

        for errors in maybe(self.errors_in(filename)):
            return sort_errors(errors)

    def errors_at(self, filename, line):
        for errors in maybe(self.errors_in(filename)):
            return errors.get(line)

    def errors_in(self, filename):
        return self._errors.get(filename)

    def clear_file(self, filename):
        for errors in [self._old_errors, self._new_errors, self._errors]:
            if filename in errors:
                del errors[filename]

    def has_errors(self):
        return len(self._errors) > 0

    def _merge_errors(self):
        self._errors = dict(list(self._old_errors.items()) + list(self._new_errors.items()))
