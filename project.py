import sublime

try:
    from .sbtsettings import SBTSettings
    from .errorreport import ErrorReport
    from .errorreporter import ErrorReporter
    from .util import maybe, OnePerWindow
except(ValueError):
    from sbtsettings import SBTSettings
    from errorreport import ErrorReport
    from errorreporter import ErrorReporter
    from util import maybe, OnePerWindow

import os
import re
from glob import glob


class Project(OnePerWindow):

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.error_report = ErrorReport()
        self.error_reporter = ErrorReporter(window,
                                            self.error_report,
                                            self.settings)

    def project_root(self):
        for folder in self.window.folders():
            if self._is_sbt_folder(folder):
                return folder

    def is_sbt_project(self):
        return self.project_root() is not None

    def is_play_project(self):
        for root in maybe(self.project_root()):
            if self._play_build_files(root):
                return True

    def sbt_command(self):
        if self.is_play_project():
            return self.settings.play_command()
        else:
            return self.settings.sbt_command()

    def setting(self, name):
        return self.settings.get(name)

    def expand_filename(self, filename):
        if len(os.path.dirname(filename)) > 0:
            return filename
        else:
            return self._find_in_project(filename)

    def relative_path(self, filename):
        return os.path.relpath(filename, self.project_root())

    def open_project_file(self, filename, line):
        full_path = os.path.join(self.project_root(), filename)
        self.window.open_file('%s:%i' % (full_path, line),
                              sublime.ENCODED_POSITION)

    def _is_sbt_folder(self, folder):
        if self._sbt_build_files(folder) or self._scala_build_files(folder):
            return True

    def _sbt_build_files(self, folder):
        return glob(os.path.join(folder, '*.sbt'))

    def _scala_build_files(self, folder):
        return glob(os.path.join(folder, 'project', '*.scala'))

    def _play_build_files(self, folder):
        return list(filter(self._is_play_build, self._scala_build_files(folder)))

    def _is_play_build(self, build_path):
        try:
            with open(build_path, 'r') as build_file:
                for line in build_file.readlines():
                    if re.search(r'\b(?:play\.|Play)Project\b', line):
                        return True
        except:
            return False

    def _find_in_project(self, filename):
        for path, _, files in os.walk(self.project_root()):
            if filename in files:
                return os.path.join(path, filename)
