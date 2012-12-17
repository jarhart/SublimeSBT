from highlighter import CodeHighlighter
from util import delayed, maybe


class ErrorMarker(object):

    def __init__(self, window, error_report):
        self._error_report = error_report
        self._highlighter = CodeHighlighter()
        self._window = window

    @delayed(0)
    def mark_errors(self):
        for view in self._window.views():
            lines = self._error_report.error_lines_in(view.file_name())
            if lines is not None:
                self._highlighter.highlight(view, lines, replace=True)
            else:
                self._highlighter.clear(view)

    @delayed(0)
    def mark_errors_in(self, filename):
        for lines in maybe(self._error_report.error_lines_in(filename)):
            for view in self._file_views(filename):
                self._highlighter.highlight(view, lines, replace=True)

    @delayed(0)
    def hide_errors_in(self, filename):
        for view in self._file_views(filename):
            self._highlighter.clear(view)

    @delayed(0)
    def mark_line(self, filename, line):
        for view in self._file_views(filename):
            self._highlighter.highlight(view, [line])

    @delayed(0)
    def clear(self):
        for view in self._window.views():
            self._highlighter.clear(view)

    @delayed(0)
    def update_status(self):
        for view in maybe(self._window.active_view()):
            error = self._line_error(self._window.active_view())
            self._highlighter.set_status_message(view, error)

    def _file_views(self, filename):
        for view in self._window.views():
            if filename == view.file_name():
                yield view

    def _line_error(self, view):
        row, _ = view.rowcol(view.sel()[0].begin())
        return self._error_report.error_at(view.file_name(), row + 1)
