import re


class BuildOutputMonitor(object):

    def __init__(self, reporter):
        self.reporter = reporter
        self._matchers = [self._match_starting,
                          self._match_error,
                          self._match_test_failure,
                          self._match_failed,
                          self._match_success]

    def __call__(self, output):
        for line in output.splitlines():
            self._output_line(self._strip_terminal_codes(line))

    def _output_line(self, line):
        for match in self._matchers:
            match(line)

    def _match_starting(self, line):
        if re.match(r'\[info\] Compiling', line):
            self.reporter.start()

    def _match_error(self, line):
        m = re.match(r'\[error\]\s+([^:]+):(\d+):\s+(.+)$', line)
        if m:
            self.reporter.error(m.group(1), int(m.group(2)), m.group(3))

    def _match_test_failure(self, line):
        m = re.match(r'\[(?:error|info)\]\s+(.+)\s+\(([^:]+):(\d+)\)$', line)
        if m:
            self.reporter.error(m.group(2), int(m.group(3)), m.group(1))

    def _match_failed(self, line):
        if re.match(r'\[error\] Total time:', line):
            self.reporter.finish()

    def _match_success(self, line):
        if re.match(r'\[success\] Total time:', line):
            self.reporter.clear()

    def _strip_terminal_codes(self, line):
        return re.sub(r'\033\[[0-9;]+m', '', line)
