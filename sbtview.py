import sublime

from sbtsettings import SBTSettings

import re


class SbtView(object):

    sbt_views = {}

    @classmethod
    def get_sbt_view(cls, window):
        if window.id() not in cls.sbt_views:
            cls.sbt_views[window.id()] = SbtView(window)
        return cls.sbt_views[window.id()]

    @classmethod
    def is_sbt_view(cls, view):
        if view is not None:
            window = view.window()
            if window is not None:
                sbt_view = cls.get_sbt_view(window)
                return sbt_view.panel.id() == view.id()

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.panel = self.window.get_output_panel('sbt')
        self._update_panel_colors()
        self.settings.add_on_change(self._update_panel_colors)
        self._output_size = 0
        self._set_running(False)

    def start(self):
        self.clear_output()
        self.show()
        self._set_running(True)

    def finish(self):
        self.show_output('\n -- Finished --\n')
        self._set_running(False)

    def show(self):
        self._update_panel_colors()
        self.window.run_command('show_panel', {'panel': 'output.sbt'})

    def hide(self):
        self.window.run_command('hide_panel', {'panel': 'output.sbt'})

    def focus(self):
        self.window.focus_view(self.panel)
        self.panel.show(self.panel.size())

    def show_output(self, output):
        output = self._clean_output(output)
        self.show()
        self._append_output(output)
        self._output_size = self.panel.size()
        self.panel.show(self.panel.size())

    def clear_output(self):
        self._erase_output(sublime.Region(0, self.panel.size()))

    def take_input(self):
        input_region = sublime.Region(self._output_size, self.panel.size())
        input = self.panel.substr(input_region)
        self._erase_output(input_region)
        return input

    def delete_left(self):
        if self.panel.sel()[0].begin() > self._output_size:
            self.panel.run_command('left_delete')

    def delete_bol(self):
        if self.panel.sel()[0].begin() >= self._output_size:
            p = self.panel.sel()[-1].end()
            self._erase_output(sublime.Region(self._output_size, p))

    def delete_word_left(self):
        if self.panel.sel()[0].begin() > self._output_size:
            for r in self.panel.sel():
                p = max(self.panel.word(r).begin(), self._output_size)
                self.panel.sel().add(sublime.Region(p, r.end()))
            self._erase_output(*self.panel.sel())

    def delete_word_right(self):
        if self.panel.sel()[0].begin() >= self._output_size:
            for r in self.panel.sel():
                p = self.panel.word(r).end()
                self.panel.sel().add(sublime.Region(r.begin(), p))
            self._erase_output(*self.panel.sel())

    def update_writability(self):
        self.panel.set_read_only(not self._running or
                                 self.panel.sel()[0].begin() < self._output_size)

    def _set_running(self, running):
        self._running = running
        self.update_writability()

    def _append_output(self, output):
        edit = self._begin_edit()
        for i, s in enumerate(output.split('\r')):
            if i > 0:
                self.panel.replace(edit, self.panel.line(self.panel.size()), s)
            else:
                self.panel.insert(edit, self.panel.size(), s)
        self._end_edit(edit)

    def _begin_edit(self):
        self.panel.set_read_only(False)
        return self.panel.begin_edit()

    def _end_edit(self, edit):
        self.panel.end_edit(edit)
        self.update_writability()

    def _erase_output(self, *regions):
        edit = self._begin_edit()
        for r in reversed(regions):
            self.panel.erase(edit, r)
        self._end_edit(edit)

    def _clean_output(self, output):
        return self._strip_codes(self._normalize_lines(output))

    def _normalize_lines(self, output):
        return output.replace('\r\n', '\n').replace('\033M\033[2K', '\r')

    def _strip_codes(self, output):
        return re.sub('\\033\[[0-9;]+m', '', output)

    def _update_panel_colors(self):
        self.panel.settings().set('color_scheme', self.settings.get('color_scheme'))
