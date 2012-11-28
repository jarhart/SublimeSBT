import sublime

from project import Project

import functools
import os
import subprocess
import thread


class SbtRunner(object):

    runners = {}

    @classmethod
    def get_runner(cls, window):
        if window.id() not in cls.runners:
            cls.runners[window.id()] = SbtRunner(window)
        return cls.runners[window.id()]

    @classmethod
    def is_sbt_running_for(cls, window):
        return cls.get_runner(window).is_sbt_running()

    def __init__(self, window):
        self.settings = sublime.load_settings('SublimeSBT.sublime-settings')
        self._project = Project.get_project(window)
        self._proc = None

    def project_root(self):
        return self._project.project_root()

    def sbt_command(self, command):
        if self._project.is_play_project():
            cmdline = self.settings.get('play_command')
        else:
            cmdline = self.settings.get('sbt_command')
        if command is not None:
            cmdline.append(command)
        return cmdline

    def start_sbt(self, command, on_start, on_stop, on_stdout, on_stderr):
        if self.project_root() and not self.is_sbt_running():
            self._start_sbt_proc(self.sbt_command(command))
            on_start()
            if self._proc.stdout:
                thread.start_new_thread(self._monitor_output, (self._proc.stdout, on_stdout))
            if self._proc.stderr:
                thread.start_new_thread(self._monitor_output, (self._proc.stderr, on_stderr))
            thread.start_new_thread(self._monitor_proc, (on_stop,))

    def stop_sbt(self):
        if self.is_sbt_running():
            self._proc.terminate()

    def kill_sbt(self):
        if self.is_sbt_running():
            self._proc.kill()

    def is_sbt_running(self):
        return (self._proc is not None) and (self._proc.returncode is None)

    def send_to_sbt(self, input):
        if self.is_sbt_running():
            self._proc.stdin.write(input)
            self._proc.stdin.flush()

    def _start_sbt_proc(self, cmdline):
        saved_cwd = os.getcwd()
        os.chdir(self.project_root())
        self._proc = subprocess.Popen(cmdline,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        os.chdir(saved_cwd)

    def _monitor_output(self, pipe, handle_output):
        while True:
            output = os.read(pipe.fileno(), 2 ** 15)
            if output != "":
                sublime.set_timeout(functools.partial(handle_output, output), 0)
            else:
                pipe.close()
                return

    def _monitor_proc(self, handle_stop):
        self._proc.wait()
        sublime.set_timeout(handle_stop, 0)