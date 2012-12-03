import sublime

import os.path


class ErrorReporter(object):

    reporters = {}

    @classmethod
    def get_reporter(cls, window):
        if window.id() not in cls.reporters:
            cls.reporters[window.id()] = ErrorReporter(window)
        return cls.reporters[window.id()]

    def __init__(self, window):
        self._window = window
        self._errors = {}
        self.settings = sublime.load_settings('SublimeSBT.sublime-settings')
        self.region_key = 'sublimesbt_error_reporting'
        self.error_scope = 'source.scala'

    def start(self):
        self._errors = {}

    def error(self, filename, line, message):
        if filename not in self._errors:
            self._errors[filename] = {}
        file_errors = self._errors[filename]
        file_errors[int(line)] = message
        self._show_error(filename, [line])

    def finish(self):
        for view in self._window.views():
            view_errors = self._view_errors(view)
            if view_errors is not None:
                lines = sorted(view_errors.keys())
                self._highlight(view, lines, replace=True)
            else:
                view.erase_regions(self.region_key)

    def clear(self):
        self._errors = {}
        self._erase_errors()

    def show_errors(self, filename):
        file_errors = self._file_errors(filename)
        if file_errors is not None:
            lines = sorted(file_errors.keys())
            for view in self._file_views(filename):
                self._highlight(view, lines, replace=True)

    def hide_errors(self, filename):
        key = self._error_key(filename)
        if key is not None:
            del self._errors[key]
        for view in self._file_views(filename):
            view.erase_regions(self.region_key)

    def update_status(self):
        view = self._window.active_view()
        view_errors = self._view_errors(view)
        if view_errors is not None:
            row, _ = view.rowcol(view.sel()[0].begin())
            line = row + 1
            if line in view_errors:
                view.set_status('SBT', view_errors[line])
            else:
                view.erase_status('SBT')

    def _show_error(self, filename, line):
        for view in self._file_views(filename):
            self._highlight(view, line)

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
            if filename in [view.file_name(), os.path.basename(view.file_name())]:
                yield view

    def _view_errors(self, view):
        return self._file_errors(view.file_name())

    def _file_errors(self, filename):
        key = self._error_key(filename)
        if key is not None:
            return self._errors[key]

    def _error_key(self, filename):
        if filename is not None:
            for f in [filename, os.path.basename(filename)]:
                if f in self._errors:
                    return f
