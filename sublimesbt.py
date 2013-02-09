import sublime_plugin
import sublime

from project import Project
from sbtrunner import SbtRunner
from sbtview import SbtView
from outputmon import BuildOutputMonitor
from util import delayed, maybe


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

    def setting(self, name):
        return self._project.setting(name)

    def _on_stdout(self, output):
        self._monitor_compile_output(output)
        self._show_output(output)

    def _on_stderr(self, output):
        self._show_output(output)

    @delayed(0)
    def _show_output(self, output):
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


class SbtTestCommand(SbtCommandCommand):

    def run(self):
        SbtCommandCommand.run(self, self.setting('test_command'))


class SbtContinuousTestCommand(SbtCommandCommand):

    def run(self):
        SbtCommandCommand.run(self, '~ ' + self.setting('test_command'))


class SbtRunCommand(SbtCommandCommand):

    def run(self):
        SbtCommandCommand.run(self, self.setting('run_command'))


class SbtErrorsCommand(SbtCommand):

    def list_errors(self):
        errors = list(self._error_report.all_errors())
        list_items = [e.list_item(self._project.relative_path) for e in errors]

        def goto_error(index):
            if index >= 0:
                self.window.open_file(errors[index].encoded_position(),
                                      sublime.ENCODED_POSITION)

        self.window.show_quick_panel(list_items, goto_error)

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
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors(view.file_name())

    def on_load(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors(view.file_name())

    def on_post_save(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.hide_errors(view.file_name())

    def on_modified(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors(view.file_name())

    def on_selection_modified(self, view):
        if SbtView.is_sbt_view(view):
            SbtView.get_sbt_view(view.window()).update_writability()
        else:
            for reporter in maybe(self._reporter(view)):
                reporter.update_status()

    def on_activated(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors(view.file_name())

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "in_sbt_view":
            if SbtView.is_sbt_view(view):
                return SbtRunner.is_sbt_running_for(view.window())
            else:
                return False

    def _reporter(self, view):
        for window in maybe(view.window()):
            return Project.get_project(window).error_reporter
