try:
    from .errormarker import ErrorMarker
    from .util import delayed
except(ValueError):
    from errormarker import ErrorMarker
    from util import delayed


class ErrorReporter(object):

    def __init__(self, window, error_report, settings):
        self._marker = ErrorMarker(window, error_report, settings)
        self._error_report = error_report

    def error(self, error):
        self._error_report.add_error(error)
        self._marker.mark_error(error)
        self._marker.update_status()

    def finish(self):
        self._error_report.cycle()
        self._marker.mark_errors()

    def clear(self):
        self._error_report.clear()
        self._marker.clear()

    def show_errors(self):
        self._marker.mark_errors()

    def show_errors_in(self, filename):
        self._marker.mark_errors_in(filename)

    def hide_errors_in(self, filename):
        self._error_report.clear_file(filename)
        self._marker.hide_errors_in(filename)

    def update_status(self):
        self._marker.update_status()

    def update_status_now(self):
        self._marker.update_status_now()
