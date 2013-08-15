try:
    from .sbterror import SbtError
    from .util import maybe
except(ValueError):
    from sbterror import SbtError
    from util import maybe

import re


class BuildOutputMonitor(object):

    def __init__(self, project):
        self.project = project
        self._parsers = [ErrorParser, TestFailureParser, FinishedParser]
        self._parser = None
        self._buffer = ''

    def __call__(self, output):
        lines = re.split(r'(?:\r\n|\n|\r)', self._buffer + output)
        self._buffer = lines[-1]
        for line in lines[0:-1]:
            self._output_line(self._strip_terminal_codes(line))

    def _output_line(self, line):
        if self._parser:
            self._parser = self._parser.parse(line)
        else:
            self._parser = self._start_parsing(line)

    def _start_parsing(self, line):
        for parser_class in self._parsers:
            for parser in parser_class.start(self.project, line):
                return parser

    def _strip_terminal_codes(self, line):
        return re.sub(r'\033(?:M|\[[0-9;]+[mK])', '', line)


class OutputParser(object):

    def parse(self, line):
        self.finish()


class AbstractErrorParser(OutputParser):

    def __init__(self, project, line, filename, lineno, message):
        self.project = project
        self.reporter = project.error_reporter
        self.filename = filename
        self.lineno = lineno
        self.message = message
        self.extra_lines = []

    def finish(self):
        self.reporter.error(self._error())

    def _extra_line(self, line):
        self.extra_lines.append(line)

    def _error(self):
        return SbtError(project=self.project,
                        filename=self.filename,
                        line=self.lineno,
                        message=self.message,
                        error_type=self.error_type,
                        extra_lines=self.extra_lines)


class ErrorParser(AbstractErrorParser):

    @classmethod
    def start(cls, project, line):
        for m in maybe(re.match(r'\[(error|warn)\]\s+(.+):(\d+):\s+(.+)$', line)):
            yield cls(project,
                      line=line,
                      label=m.group(1),
                      filename=m.group(2),
                      lineno=int(m.group(3)),
                      message=m.group(4))

    def __init__(self, project, line, label, filename, lineno, message):
        AbstractErrorParser.__init__(self, project, line, filename, lineno, message)
        if label == 'warn':
            self.error_type = 'warning'
        else:
            self.error_type = 'error'

    def parse(self, line):
        for t in maybe(self._match_last_line(line)):
            self._extra_line(t)
            return self.finish()
        for t in maybe(self._match_line(line)):
            self._extra_line(t)
            return self
        return self.finish()

    def _match_last_line(self, line):
        for m in maybe(re.match(r'\[(?:error|warn)\] (\s*\^\s*)$', line)):
            return m.group(1)

    def _match_line(self, line):
        for m in maybe(re.match(r'\[(?:error|warn)\] (.*)$', line)):
            return m.group(1)


class TestFailureParser(AbstractErrorParser):

    @classmethod
    def start(cls, project, line):
        for m in maybe(re.match(r'\[(?:error|info)\]\s+(.+)\s+\(([^:]+):(\d+)\)$', line)):
            yield cls(project,
                      line=line,
                      filename=m.group(2),
                      lineno=int(m.group(3)),
                      message=m.group(1))

    def __init__(self, project, line, filename, lineno, message):
        AbstractErrorParser.__init__(self, project, line, filename, lineno, message)
        self.error_type = 'failure'


class FinishedParser(OutputParser):

    @classmethod
    def start(cls, project, line):
        if re.match(r'\[(?:success|error)\] Total time:', line):
            yield cls(project)

    def __init__(self, project):
        self.reporter = project.error_reporter

    def finish(self):
        self.reporter.finish()
