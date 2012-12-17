from errormarker import ErrorMarker

from util import delayed


class ErrorReporter(object):

    def __init__(self, window, error_report, expand_filename):
        self._marker = ErrorMarker(window, error_report)
        self._error_report = error_report
        self._expand_filename = expand_filename

    def start(self):
        self._error_report.clear()

    @delayed(0)
    def error(self, filename, line, message):
        filename = self._expand_filename(filename)
        self._error_report.add_error(filename, line, message)
        self._marker.mark_line(filename, line)
        self._marker.update_status()

    def finish(self):
        self._marker.mark_errors()

    def clear(self):
        self._error_report.clear()
        self._marker.clear()

    def show_errors(self, filename):
        self._marker.mark_errors_in(filename)

    def hide_errors(self, filename):
        self._error_report.clear_file(filename)
        self._marker.hide_errors_in(filename)

    def update_status(self):
        self._marker.update_status()
