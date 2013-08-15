import sublime
import sublime_plugin

try:
    from .sbtsettings import SBTSettings
    from .util import maybe, OnePerWindow
except(ValueError):
    from sbtsettings import SBTSettings
    from util import maybe, OnePerWindow

import re


class SbtView(OnePerWindow):

    settings = {
        "line_numbers": False,
        "gutter": False,
        "rulers": [],
        "word_wrap": False,
        "draw_centered": False,
        "highlight_line": False
    }

    @classmethod
    def is_sbt_view(cls, view):
        if view is not None:
            for window in maybe(view.window()):
                sbt_view = cls(window)
                return sbt_view.panel.id() == view.id()

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.panel = self.window.get_output_panel('sbt')
        self.panel.set_syntax_file("Packages/SublimeSBT/SBTOutput.hidden-tmLanguage")
        for name, setting in SbtView.settings.items():
            self.panel.settings().set(name, setting)
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
        if sublime.platform() == 'windows':
            self._append_output('\n')
        else:
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
        self._run_command('sbt_append_output', output=output)

    def _erase_output(self, *regions):
        self._run_command('sbt_erase_output',
                          regions=[[r.begin(), r.end()] for r in regions])

    def _run_command(self, name, **kwargs):
        self.panel.set_read_only(False)
        self.panel.run_command(name, kwargs)
        self.update_writability()

    def _clean_output(self, output):
        return self._strip_codes(self._normalize_lines(output))

    def _normalize_lines(self, output):
        return output.replace('\r\n', '\n').replace('\033M', '\r')

    def _strip_codes(self, output):
        return re.sub(r'\033\[[0-9;]+[mK]', '', output)

    def _update_panel_colors(self):
        self.panel.settings().set('color_scheme', self.settings.get('color_scheme'))


class SbtAppendOutputCommand(sublime_plugin.TextCommand):

    def run(self, edit, output):
        for i, s in enumerate(output.split('\r')):
            if i > 0:
                self.view.replace(edit, self.view.line(self.view.size()), s)
            else:
                self.view.insert(edit, self.view.size(), s)


class SbtEraseOutputCommand(sublime_plugin.TextCommand):

    def run(self, edit, regions):
        for a, b in reversed(regions):
            self.view.erase(edit, sublime.Region(int(a), int(b)))
