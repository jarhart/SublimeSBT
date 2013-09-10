import sublime
import sublime_plugin

try:
    from .sbtsettings import SBTSettings
    from .util import OnePerWindow
except(ValueError):
    from sbtsettings import SBTSettings
    from util import OnePerWindow


class ErrorView(OnePerWindow):

    error_type_display = {
        'error': 'Error',
        'warning': 'Warning',
        'failure': 'Test Failure'
    }

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.panel = self.window.get_output_panel('sbt_error')
        self.panel.set_read_only(True)
        self.panel.settings().set('line_numbers', False)
        self.panel.settings().set('gutter', False)
        self.panel.settings().set('scroll_past_end', False)
        self.panel.set_syntax_file("Packages/SublimeSBT/SBTError.hidden-tmLanguage")
        self._update_panel_colors()
        self.settings.add_on_change(self._update_panel_colors)

    def show(self):
        self._update_panel_colors()
        self.window.run_command('show_panel', {'panel': 'output.sbt_error'})

    def hide(self):
        self.window.run_command('hide_panel', {'panel': 'output.sbt_error'})

    def show_error(self, error):
        self.show()
        self.panel.run_command('sbt_show_error_text',
                               {'text': self._error_text(error)})
        self.panel.sel().clear()
        self.panel.show(0)

    def _error_text(self, error):
        banner = ' -- %s --' % type(self).error_type_display[error.error_type]
        return '%s\n%s' % (banner, error.text)

    def _update_panel_colors(self):
        self.panel.settings().set('color_scheme', self.settings.get('color_scheme'))


class SbtShowErrorTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, text):
        self.view.set_read_only(False)
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)
        self.view.set_read_only(True)
