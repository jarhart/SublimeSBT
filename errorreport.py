from util import maybe


class ErrorReport(object):

    def __init__(self):
        self._errors = {}

    def clear(self):
        self._errors.clear()

    def add_error(self, filename, line, message):
        if filename not in self._errors:
            self._errors[filename] = {}
        file_errors = self._errors[filename]
        file_errors[int(line)] = message

    def all_errors(self):
        for filename in sorted(self._errors.keys()):
            for line in sorted(self._errors[filename].keys()):
                yield (filename, line, self._errors[filename][line])

    def error_lines_in(self, filename):
        for errors in maybe(self.errors_in(filename)):
            return sorted(errors.keys())

    def error_at(self, filename, line):
        for errors in maybe(self.errors_in(filename)):
            return errors.get(line)

    def errors_in(self, filename):
        return self._errors.get(filename)

    def clear_file(self, filename):
        if filename in self._errors:
            del self._errors[filename]

    def has_errors(self):
        return len(self._errors) > 0
