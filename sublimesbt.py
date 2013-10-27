import sublime_plugin
import sublime

try:
    from .project import Project
    from .sbtrunner import SbtRunner
    from .sbtview import SbtView
    from .errorview import ErrorView
    from .outputmon import BuildOutputMonitor
    from .util import delayed, maybe
except(ValueError):
    from project import Project
    from sbtrunner import SbtRunner
    from sbtview import SbtView
    from errorview import ErrorView
    from outputmon import BuildOutputMonitor
    from util import delayed, maybe

class SbtWindowCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args):
        super(SbtWindowCommand, self).__init__(*args)
        self._project = Project(self.window)
        self._runner = SbtRunner(self.window)
        self._sbt_view = SbtView(self.window)
        self._error_view = ErrorView(self.window)
        self._error_reporter = self._project.error_reporter
        self._error_report = self._project.error_report
        self._monitor_compile_output = BuildOutputMonitor(self._project)

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

    @delayed(0)
    def show_error(self, error):
        self._error_report.focus_error(error)
        self._error_reporter.show_errors()
        self._error_view.show_error(error)
        self.goto_error(error)

    @delayed(0)
    def goto_error(self, error):
        self.window.open_file(error.encoded_position(), sublime.ENCODED_POSITION)

    def show_error_output(self):
        self._error_view.show()

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


class StartSbtCommand(SbtWindowCommand):

    def run(self):
        self.start_sbt()

    def is_enabled(self):
        return self.is_sbt_project() and not self.is_sbt_running()


class StopSbtCommand(SbtWindowCommand):

    def run(self):
        self.stop_sbt()

    def is_enabled(self):
        return self.is_sbt_running()


class KillSbtCommand(SbtWindowCommand):

    def run(self):
        self.kill_sbt()

    def is_enabled(self):
        return self.is_sbt_running()


class ShowSbtCommand(SbtWindowCommand):

    def run(self):
        self.show_sbt()
        self.focus_sbt()

    def is_enabled(self):
        return self.is_sbt_project()


class SbtSubmitCommand(SbtWindowCommand):

    def run(self):
        self.send_to_sbt(self.take_input() + '\n')

    def is_enabled(self):
        return self.is_sbt_running()


class SbtCommand(SbtWindowCommand):

    def run(self, command):
        if self.is_sbt_running():
            self.send_to_sbt(command + '\n')
        else:
            self.start_sbt(command)

    def is_enabled(self):
        return self.is_sbt_project()


class SbtTestCommand(SbtCommand):

    def run(self):
        super(SbtTestCommand, self).run(self.test_command())

    def test_command(self):
        return self.setting('test_command')


class SbtContinuousTestCommand(SbtTestCommand):

    def test_command(self):
        return '~ ' + super(SbtContinuousTestCommand, self).test_command()


test_only_arg = '*'


class SbtTestOnlyCommand(SbtCommand):

    base_command = 'test-only'

    def run(self):
        self.window.show_input_panel(self.prompt(), test_only_arg,
                                     self.test_only, None, None)

    def test_only(self, arg):
        global test_only_arg
        test_only_arg = arg
        super(SbtTestOnlyCommand, self).run(self.test_command(arg))

    def prompt(self):
        return 'SBT: %s' % self.base_command

    def test_command(self, arg):
        return '%s %s' % (self.base_command, arg)


class SbtContinuousTestOnlyCommand(SbtTestOnlyCommand):

    def test_command(self, arg):
        return '~ ' + super(SbtContinuousTestOnlyCommand, self).test_command(arg)


class SbtTestQuickCommand(SbtTestOnlyCommand):

    base_command = 'test-quick'


class SbtContinuousTestQuickCommand(SbtTestQuickCommand):

    def test_command(self, arg):
        return '~ ' + super(SbtContinuousTestQuickCommand, self).test_command(arg)


class SbtRunCommand(SbtCommand):

    def run(self):
        super(SbtRunCommand, self).run(self.setting('run_command'))


class SbtReloadCommand(SbtCommand):

    def run(self):
        super(SbtReloadCommand, self).run('reload')

    def is_enabled(self):
        return self.is_sbt_running()


class SbtErrorsCommand(SbtWindowCommand):

    def is_enabled(self):
        return self.is_sbt_project() and self._error_report.has_errors()


class ClearSbtErrorsCommand(SbtErrorsCommand):

    def run(self):
        self._error_reporter.clear()


class ListSbtErrorsCommand(SbtErrorsCommand):

    def run(self):
        errors = list(self._error_report.all_errors())
        list_items = [e.list_item() for e in errors]

        def goto_error(index):
            if index >= 0:
                self.show_error(errors[index])

        self.window.show_quick_panel(list_items, goto_error)


class NextSbtErrorCommand(SbtErrorsCommand):

    def run(self):
        self.show_error(self._error_report.next_error())


class ShowSbtErrorOutputCommand(SbtErrorsCommand):

    def run(self):
        self.show_error_output()


class SbtEotCommand(SbtWindowCommand):

    def run(self):
        if sublime.platform() == 'windows':
            self.send_to_sbt('\032')
        else:
            self.send_to_sbt('\004')

    def is_enabled(self):
        return self.is_sbt_running()


class SbtDeleteLeftCommand(SbtWindowCommand):

    def run(self):
        self._sbt_view.delete_left()


class SbtDeleteBolCommand(SbtWindowCommand):

    def run(self):
        self._sbt_view.delete_bol()


class SbtDeleteWordLeftCommand(SbtWindowCommand):

    def run(self):
        self._sbt_view.delete_word_left()


class SbtDeleteWordRightCommand(SbtWindowCommand):

    def run(self):
        self._sbt_view.delete_word_right()


class SbtListener(sublime_plugin.EventListener):

    def on_clone(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors_in(view.file_name())

    def on_load(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors_in(view.file_name())

    def on_post_save(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.hide_errors_in(view.file_name())

    def on_modified(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors_in(view.file_name())

    def on_selection_modified(self, view):
        if SbtView.is_sbt_view(view):
            SbtView(view.window()).update_writability()
        else:
            for reporter in maybe(self._reporter(view)):
                reporter.update_status_now()

    def on_activated(self, view):
        for reporter in maybe(self._reporter(view)):
            reporter.show_errors_in(view.file_name())

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == "in_sbt_view":
            if SbtView.is_sbt_view(view):
                return SbtRunner.is_sbt_running_for(view.window())
            else:
                return False

    def _reporter(self, view):
        for window in maybe(view.window()):
            return Project(window).error_reporter
