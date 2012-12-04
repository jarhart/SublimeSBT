from sbtsettings import SBTSettings

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
