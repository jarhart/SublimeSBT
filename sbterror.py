try:
    from .util import delayed
except(ValueError):
    from util import delayed

from threading import Event

import re

class SbtError(object):

    def __init__(self, project, filename, line, message, error_type, extra_lines):
        self.line = int(line)
        if len(extra_lines) > 0 and re.match(r' *^', extra_lines[-1]):
            self.column = len(extra_lines[-1])
        else:
            self.column = 1
        self.message = message
        self.error_type = error_type
        self.__finished = Event()
        self.__finish(project, filename, extra_lines)

    @property
    def filename(self):
        self.__finished.wait()
        return self.__filename

    @property
    def relative_path(self):
        self.__finished.wait()
        return self.__relative_path

    @property
    def text(self):
        self.__finished.wait()
        return self.__text

    def list_item(self):
        return [self.message, '%s:%i:%i' % (self.relative_path, self.line, self.column)]

    def encoded_position(self):
        return '%s:%i:%i' % (self.filename, self.line, self.column)

    @delayed(0)
    def __finish(self, project, filename, extra_lines):
        try:
            self.__filename = project.expand_filename(filename)
            self.__relative_path = project.relative_path(self.__filename)
            if self.error_type == 'failure':
                self.__text = '%s (%s:%i)' % (self.message, filename, self.line)
            else:
                extra_lines.insert(0, '%s:%i: %s' % (self.__relative_path, self.line, self.message))
                self.__text = '\n'.join(extra_lines)
        finally:
            self.__finished.set()
