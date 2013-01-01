import sublime

from util import maybe


class SBTSettings(object):

    def __init__(self, window):
        self.window = window
        self._plugin_settings = sublime.load_settings('SublimeSBT.sublime-settings')

    def sbt_command(self):
        return self._view_settings().get('sbt_command', self._plugin_settings.get('sbt_command'))

    def play_command(self):
        return self._view_settings().get('sbt_command', self._plugin_settings.get('play_command'))

    def color_scheme(self):
        self.get('color_scheme')

    def get(self, name):
        return self._view_settings().get(name, self._plugin_settings.get(name))

    def add_on_change(self, on_change):
        self._plugin_settings.add_on_change('SublimeSBT', on_change)

    def _view_settings(self):
        for view in maybe(self.window.active_view()):
            return view.settings().get('SublimeSBT', {})
        return {}
