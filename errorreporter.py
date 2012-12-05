import sublime


class ErrorReporter(object):

    def __init__(self, window, error_report, expand_filename):
        self._window = window
        self._error_report = error_report
        self._expand_filename = expand_filename
        self.region_key = 'sublimesbt_error_reporting'
        self.error_scope = 'source.scala'

    def start(self):
        self._error_report.clear()

    def error(self, filename, line, message):
        filename = self._expand_filename(filename)
        self._error_report.add_error(filename, line, message)
        self._highlight_error(filename, line)
        self.update_status()

    def finish(self):
        for view in self._window.views():
            view_errors = self._error_report.errors_in(view.file_name())
            if view_errors is not None:
                lines = sorted(view_errors.keys())
                self._highlight(view, lines, replace=True)
            else:
                view.erase_regions(self.region_key)

    def clear(self):
        self._error_report.clear()
        self._erase_errors()

    def show_errors(self, filename):
        file_errors = self._error_report.errors_in(filename)
        if file_errors is not None:
            lines = sorted(file_errors.keys())
            for view in self._file_views(filename):
                self._highlight(view, lines, replace=True)

    def hide_errors(self, filename):
        self._error_report.clear_file(filename)
        for view in self._file_views(filename):
            view.erase_regions(self.region_key)

    def update_status(self):
        view = self._window.active_view()
        if view is not None:
            error = self._line_error(self._window.active_view())
            if error is not None:
                view.set_status('SBT', error)
            else:
                view.erase_status('SBT')

    def _highlight_error(self, filename, line):
        for view in self._file_views(filename):
            self._highlight(view, [line])

    def _highlight(self, view, lines, replace=False):
        if replace:
            regions = []
        else:
            regions = view.get_regions(self.region_key)
        regions.extend([view.line(view.text_point(l - 1, 0)) for l in lines])
        view.add_regions(self.region_key, regions, self.error_scope, sublime.DRAW_OUTLINED)

    def _erase_errors(self):
        for view in self._window.views():
            view.erase_regions(self.region_key)

    def _file_views(self, filename):
        for view in self._window.views():
            if filename == view.file_name():
                yield view

    def _line_error(self, view):
        row, _ = view.rowcol(view.sel()[0].begin())
        return self._error_report.error_at(view.file_name(), row + 1)
