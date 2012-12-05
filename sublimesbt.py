import sublime_plugin
import sublime

from project import Project
from sbtrunner import SbtRunner
from sbtview import SbtView
from outputmon import BuildOutputMonitor

import functools


class SbtCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args):
        super(SbtCommand, self).__init__(*args)
        self._project = Project.get_project(self.window)
        self._runner = SbtRunner.get_runner(self.window)
        self._sbt_view = SbtView.get_sbt_view(self.window)
        self._error_reporter = self._project.error_reporter
        self._error_report = self._project.error_report
        self._monitor_compile_output = BuildOutputMonitor(self._error_reporter)

    def is_sbt_project(self):
        return self._project.is_sbt_project()

    def is_play_project(self):
        return self._project.is_play_project()

    def is_sbt_running(self):
        return self._runner.is_sbt_running()

    def start_sbt(self, command=None):
        self._runner.start_sbt(command,
                               on_start=self._sbt_view.start,
                               on_stop=self._sbt_view.finish,
                               on_stdout=self._on_stdout,
                               on_stderr=self._on_stderr)

    def stop_sbt(self):
        self._runner.stop_sbt()

    def kill_sbt(self):
        self._runner.kill_sbt()

    def show_sbt(self):
        self._sbt_view.show()

    def hide_sbt(self):
        self._sbt_view.hide()

    def focus_sbt(self):
        self._sbt_view.focus()

    def take_input(self):
        return self._sbt_view.take_input()

    def send_to_sbt(self, cmd):
        self._runner.send_to_sbt(cmd)

    def _on_stdout(self, output):
        self._monitor_compile_output(output)
        self._sbt_view.show_output(output)

    def _on_stderr(self, output):
        self._sbt_view.show_output(output)


class StartSbtCommand(SbtCommand):

    def run(self):
        self.start_sbt()

    def is_enabled(self):
        return self.is_sbt_project() and not self.is_sbt_running()


class StopSbtCommand(SbtCommand):

    def run(self):
        self.stop_sbt()

    def is_enabled(self):
        return self.is_sbt_running()


class KillSbtCommand(SbtCommand):

    def run(self):
        self.kill_sbt()

    def is_enabled(self):
        return self.is_sbt_running()


class ShowSbtCommand(SbtCommand):

    def run(self):
        self.show_sbt()
        self.focus_sbt()

    def is_enabled(self):
        return self.is_sbt_project()


class SbtSubmitCommand(SbtCommand):

    def run(self):
        self.send_to_sbt(self.take_input() + '\n')

    def is_enabled(self):
        return self.is_sbt_running()


class SbtCommandCommand(SbtCommand):

    def run(self, command):
        if self.is_sbt_running():
            self.send_to_sbt(command + '\n')
        else:
            self.start_sbt(command)

    def is_enabled(self):
        return self.is_sbt_project()


class SbtErrorsCommand(SbtCommand):

    def list_errors(self):
        errors = list(self._error_report.all_errors())

        def goto_error(index):
            if index >= 0:
                filename, line, _ = errors[index]
                self.window.open_file('%s:%i' % (filename, line),
                                      sublime.ENCODED_POSITION)

        def list_item((filename, line, message)):
            relative_path = self._project.relative_path(filename)
            return [message, '%s:%i' % (relative_path, line)]

        self.window.show_quick_panel([list_item(e) for e in errors], goto_error)

    def is_enabled(self):
        return self.is_sbt_project() and self._error_report.has_errors()


class ClearSbtErrorsCommand(SbtErrorsCommand):

    def run(self):
        self._error_reporter.clear()


class ListSbtErrorsCommand(SbtErrorsCommand):

    def run(self):
        self.list_errors()


class SbtEotCommand(SbtCommand):

    def run(self):
        if sublime.platform() == 'windows':
            self.send_to_sbt('\032')
        else:
            self.send_to_sbt('\004')

    def is_enabled(self):
        return self.is_sbt_running()


class SbtDeleteLeftCommand(SbtCommand):

    def run(self):
        self._sbt_view.delete_left()


class SbtDeleteBolCommand(SbtCommand):

    def run(self):
        self._sbt_view.delete_bol()


class SbtDeleteWordLeftCommand(SbtCommand):

    def run(self):
        self._sbt_view.delete_word_left()


class SbtDeleteWordRightCommand(SbtCommand):

    def run(self):
        self._sbt_view.delete_word_right()


class SbtListener(sublime_plugin.EventListener):

    def on_clone(self, view):
        self._with_window(view, self._show_errors)

    def on_load(self, view):
        self._with_window(view, self._show_errors)

    def on_post_save(self, view):
        self._with_window(view, self._hide_errors)

    def on_selection_modified(self, view):
        if SbtView.is_sbt_view(view):
            SbtView.get_sbt_view(view.window()).update_writability()
        else:
            self._with_window(view, self._update_status)

    def on_activated(self, view):
        self._with_window(view, self._show_errors)

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "in_sbt_view":
            if SbtView.is_sbt_view(view):
                return SbtRunner.is_sbt_running_for(view.window())
            else:
                return False

    def _show_errors(self, view, window):
        self._get_reporter(window).show_errors(view.file_name())

    def _hide_errors(self, view, window):
        self._get_reporter(window).hide_errors(view.file_name())

    def _update_status(self, view, window):
        self._get_reporter(window).update_status()

    def _get_reporter(self, window):
        return Project.get_project(window).error_reporter

    def _with_window(self, view, f, retries=2):
        window = view.window()
        if window is not None:
            f(view, window)
        elif retries > 0:
            sublime.set_timeout(functools.partial(self._with_window, view, f,
                                                  retries - 1),
                                100)
