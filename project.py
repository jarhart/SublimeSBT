import sublime

from sbtsettings import SBTSettings

from errorreport import ErrorReport
from errorreporter import ErrorReporter

import os
import re


class Project(object):

    projects = {}

    @classmethod
    def get_project(cls, window):
        if window.id() not in cls.projects:
            cls.projects[window.id()] = Project(window)
        return cls.projects[window.id()]

    def __init__(self, window):
        self.window = window
        self.settings = SBTSettings(window)
        self.error_report = ErrorReport()
        self.error_reporter = ErrorReporter(window, self.error_report, self.expand_filename)

    def project_root(self):
        for folder in self.window.folders():
            if self._is_sbt_folder(folder):
                return folder

    def is_sbt_project(self):
        return self.project_root() is not None

    def is_play_project(self):
        if not self.is_sbt_project():
            return False
        build_path = os.path.join(self.project_root(), 'project', 'Build.scala')
        return os.path.exists(build_path) and self._is_play_build(build_path)

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
        return (os.path.exists(os.path.join(folder, 'build.sbt')) or
                os.path.exists(os.path.join(folder, 'project', 'Build.scala')))

    def _is_play_build(self, build_path):
        try:
            build_file = open(build_path, 'r').readlines()
            for line in build_file:
                if re.search(r'\bPlayProject\b', line):
                    return True
            build_file.close()
        except:
            return False

    def _find_in_project(self, filename):
        for path, _, files in os.walk(self.project_root()):
            if filename in files:
                return os.path.join(path, filename)
