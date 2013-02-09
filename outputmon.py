try:
    from .util import maybe
except(ValueError):
    from util import maybe

import re


class BuildOutputMonitor(object):

    def __init__(self, reporter):
        self.reporter = reporter
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
            for parser in parser_class.start(self.reporter, line):
                return parser

    def _strip_terminal_codes(self, line):
        return re.sub(r'\033\[[0-9;]+m', '', line)


class OutputParser(object):

    def parse(self, line):
        self.finish()


class AbstractErrorParser(OutputParser):

    def __init__(self, reporter, line, filename, lineno, message):
        self.reporter = reporter
        self.filename = filename
        self.lineno = lineno
        self.message = message
        self.text = []

    def finish(self):
        self.reporter.error(self.filename, self.lineno, self.message, self.error_type)


class ErrorParser(AbstractErrorParser):

    @classmethod
    def start(cls, reporter, line):
        for m in maybe(re.match(r'\[(error|warn)\]\s+(.+):(\d+):\s+(.+)$', line)):
            yield cls(reporter,
                      line=line,
                      label=m.group(1),
                      filename=m.group(2),
                      lineno=int(m.group(3)),
                      message=m.group(4))

    def __init__(self, reporter, line, label, filename, lineno, message):
        AbstractErrorParser.__init__(self, reporter, line, filename, lineno, message)
        if label == 'warn':
            self.error_type = 'warning'
        else:
            self.error_type = 'error'
        for t in maybe(self._match_line(line)):
            self.text.append(t)

    def parse(self, line):
        for p in maybe(self._match_last_line(line)):
            self.col = p
            return self.finish()
        for t in maybe(self._match_line(line)):
            self.text.append(t)
            return self
        return self.finish()

    def _match_last_line(self, line):
        for m in maybe(re.match(r'\[(?:error|warn)\]\s(\s*)\^\s*$', line)):
            yield len(m.group(1))

    def _match_line(self, line):
        for m in maybe(re.match(r'\[(?:error|warn)\] (.*)$', line)):
            yield m.group(1)


class TestFailureParser(AbstractErrorParser):

    @classmethod
    def start(cls, reporter, line):
        for m in maybe(re.match(r'\[(?:error|info)\]\s+(.+)\s+\(([^:]+):(\d+)\)$', line)):
            yield cls(reporter,
                      line=line,
                      filename=m.group(2),
                      lineno=m.group(3),
                      message=m.group(1))

    def __init__(self, reporter, line, filename, lineno, message):
        AbstractErrorParser.__init__(self, reporter, line, filename, lineno, message)
        self.error_type = 'failure'


class FinishedParser(OutputParser):

    @classmethod
    def start(cls, reporter, line):
        if re.match(r'\[(?:success|error)\] Total time:', line):
            yield cls(reporter)

    def __init__(self, reporter):
        self.reporter = reporter

    def finish(self):
        self.reporter.finish()
