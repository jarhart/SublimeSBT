import sublime

try:
    from .util import maybe
except(ValueError):
    from util import maybe


class SBTSettings(object):

    def __init__(self, window):
        self.window = window
        self._plugin_settings = sublime.load_settings('SublimeSBT.sublime-settings')
        self._migrate_user_config()

    def sbt_command(self):
        return self.get('sbt_command')

    def play_command(self):
        return self._view_settings().get('sbt_command', self._plugin_settings.get('play_command'))

    def test_command(self):
        return self.get('test_command')

    def run_command(self):
        return self.get('run_command')

    def mark_style(self, error_type='error'):
        self.mark_settings(error_type).get('style')

    def error_scope(self, error_type='error'):
        self.mark_settings(error_type).get('scope')

    def color_scheme(self):
        return self.get('color_scheme')

    def mark_settings(self, error_type='error'):
        for settings in maybe(self.get('%s_marking' % error_type)):
            return settings
        return self.global_mark_settings()

    def global_mark_settings(self):
        return {
            'style': self.get('mark_style'),
            'scope': self.get('error_scope')
        }

    def get(self, name):
        return self._view_settings().get(name, self._plugin_settings.get(name))

    def add_on_change(self, on_change):
        self._plugin_settings.add_on_change('SublimeSBT', on_change)

    def _view_settings(self):
        for view in maybe(self.window.active_view()):
            return view.settings().get('SublimeSBT', {})
        return {}

    def _migrate_user_config(self):
        style = self._plugin_settings.get('mark_style', None)
        scope = self._plugin_settings.get('error_scope', None)
        if style is not None or scope is not None:
            for key in ('%s_marking' % t for t in ('error', 'failure', 'warning')):
                mark_settings = self._plugin_settings.get(key, {})
                if style is not None:
                    mark_settings['style'] = style
                if scope is not None:
                    mark_settings['scope'] = scope
                self._plugin_settings.set(key, mark_settings)
            self._plugin_settings.erase('mark_style')
            self._plugin_settings.erase('error_scope')
            sublime.save_settings('SublimeSBT.sublime-settings')
