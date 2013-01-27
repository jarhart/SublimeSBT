from util import maybe


class ErrorReport(object):

    def __init__(self):
        self._errors = {}
        self._old_errors = {}
        self._new_errors = {}

    def clear(self):
        self._errors.clear()
        self._old_errors.clear()
        self._new_errors.clear()

    def add_error(self, filename, line, message):
        if filename not in self._new_errors:
            self._new_errors[filename] = {}
        file_errors = self._new_errors[filename]
        lineno = int(line)
        if lineno not in file_errors:
            file_errors[lineno] = []
        file_errors[lineno].append(message)
        self._merge_errors()

    def cycle(self):
        self._old_errors = self._new_errors
        self._new_errors = {}
        self._merge_errors()

    def all_errors(self):
        for filename in sorted(self._errors.keys()):
            for line in sorted(self._errors[filename].keys()):
                for message in self._errors[filename][line]:
                    yield (filename, line, message)

    def error_lines_in(self, filename):
        for errors in maybe(self.errors_in(filename)):
            return sorted(errors.keys())

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
        self._errors = dict(self._old_errors.items() + self._new_errors.items())
