import sublime
import sublime_plugin

try:
    from .sbtsettings import SBTSettings
except(ValueError):
    from sbtsettings import SBTSettings


class ErrorView(object):

    error_views = {}

    @classmethod
    def get_error_view(cls, window):
        if window.id() not in cls.error_views:
            cls.error_views[window.id()] = ErrorView(window)
        return cls.error_views[window.id()]

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.panel = self.window.get_output_panel('sbt_error')
        self.panel.set_read_only(True)
        self._update_panel_colors()
        self.settings.add_on_change(self._update_panel_colors)
        self._type_display = {
            'error': 'Error',
            'warning': 'Warning',
            'failure': 'Test Failure'
        }

    def show(self):
        self._update_panel_colors()
        self.window.run_command('show_panel', {'panel': 'output.sbt_error'})

    def hide(self):
        self.window.run_command('hide_panel', {'panel': 'output.sbt_error'})

    def show_error(self, error):
        banner = ' -- %s --' % self._type_display[error.error_type]
        text = '%s\n\n%s' % (banner, error.text)
        self.show()
        self.panel.run_command('sbt_show_error_text', {'text': text})
        self.panel.sel().clear()
        self.panel.show(0)

    def _update_panel_colors(self):
        self.panel.settings().set('color_scheme', self.settings.get('color_scheme'))


class SbtShowErrorTextCommand(sublime_plugin.TextCommand):

    def run(self, edit, text):
        self.view.set_read_only(False)
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)
        self.view.set_read_only(True)
