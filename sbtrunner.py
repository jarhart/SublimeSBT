import sublime

try:
    from .project import Project
    from .util import OnePerWindow
except(ValueError):
    from project import Project
    from util import OnePerWindow

import os
import pipes
import signal
import subprocess
import threading


class SbtRunner(OnePerWindow):

    @classmethod
    def is_sbt_running_for(cls, window):
        return cls(window).is_sbt_running()

    def __init__(self, window):
        self._project = Project(window)
        self._proc = None
        self._history = []

    def project_root(self):
        return self._project.project_root()

    def sbt_command(self, command):
        cmdline = self._project.sbt_command()
        if command is not None:
            cmdline.append(command)
        return cmdline

    def start_sbt(self, command, on_start, on_stop, on_stdout, on_stderr):
        if self.project_root() and not self.is_sbt_running():
            self._proc = self._try_start_sbt_proc(self.sbt_command(command),
                                                  on_start,
                                                  on_stop,
                                                  on_stdout,
                                                  on_stderr)

    def stop_sbt(self):
        if self.is_sbt_running():
            self._proc.terminate()

    def kill_sbt(self):
        if self.is_sbt_running():
            self._proc.kill()

    def is_sbt_running(self):
        return (self._proc is not None) and self._proc.is_running()

    def send_to_sbt(self, input):
        if self.is_sbt_running():
            self.add_to_history(input)
            self._proc.send(input)

    def _try_start_sbt_proc(self, cmdline, *handlers):
        try:
            return SbtProcess.start(cmdline,
                                    self.project_root(),
                                    self._project.settings,
                                    *handlers)
        except OSError:
            msg = ('Unable to find "%s".\n\n'
                   'You may need to specify the full path to your sbt command.'
                   % cmdline[0])
            sublime.error_message(msg)

    def add_to_history(self, input):
        if input != '' and not input.isspace ():
            input = input.rstrip('\n\r')
            self._history = [cmd for cmd in self._history if cmd != input]
            self._history.insert (0, input)
            history_length = self._project.settings.get('history_length') or 20
            del self._history[history_length:]

    def clear_history(self):
        self._history.clear ()

    def get_history(self):
        return self._history


class SbtProcess(object):

    @staticmethod
    def start(*args, **kwargs):
        if sublime.platform() == 'windows':
            return SbtWindowsProcess._start(*args, **kwargs)
        else:
            return SbtUnixProcess._start(*args, **kwargs)

    @classmethod
    def _start(cls, cmdline, cwd, settings, *handlers):
        return cls(cls._start_proc(cmdline, cwd, settings), settings, *handlers)

    @classmethod
    def _start_proc(cls, cmdline, cwd, settings):
        return cls._popen(cmdline,
                          env=cls._sbt_env(settings),
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=cwd)

    @classmethod
    def _sbt_env(cls, settings):
        return dict(list(os.environ.items()) +
                    [cls._append_opts('SBT_OPTS', cls._sbt_opts(settings))])

    @classmethod
    def _sbt_opts(cls, settings):
        return [
            str('-Dfile.encoding=%s' % (settings.get('encoding') or 'UTF-8'))
        ]

    @classmethod
    def _append_opts(cls, name, opts):
        existing_opts = os.environ.get(name, None)
        if existing_opts:
            opts = [existing_opts] + opts
        return [name, ' '.join(opts)]

    def __init__(self, proc, settings, on_start, on_stop, on_stdout, on_stderr):
        self._proc = proc
        self._encoding = settings.get('encoding') or 'UTF-8'
        on_start()
        if self._proc.stdout:
            self._start_thread(self._monitor_output,
                               (self._proc.stdout, on_stdout))
        if self._proc.stderr:
            self._start_thread(self._monitor_output,
                               (self._proc.stderr, on_stderr))
        self._start_thread(self._monitor_proc, (on_stop,))

    def is_running(self):
        return self._proc.returncode is None

    def send(self, input):
        self._proc.stdin.write(input.encode())
        self._proc.stdin.flush()

    def _monitor_output(self, pipe, handle_output):
        while True:
            output = os.read(pipe.fileno(), 2 ** 15).decode(self._encoding)
            if output != "":
                handle_output(output)
            else:
                pipe.close()
                return

    def _monitor_proc(self, handle_stop):
        self._proc.wait()
        sublime.set_timeout(handle_stop, 0)

    def _start_thread(self, target, args):
        threading.Thread(target=target, args=args).start()


class SbtUnixProcess(SbtProcess):

    @classmethod
    def _popen(cls, cmdline, **kwargs):
        return subprocess.Popen(cls._shell_cmdline(cmdline),
                                preexec_fn=os.setpgrp,
                                **kwargs)

    @classmethod
    def _shell_cmdline(cls, cmdline):
        shell = os.environ.get('SHELL', '/bin/bash')
        opts = '-ic' if shell.endswith('csh') else '-lic'
        cmd = ' '.join(map(pipes.quote, cmdline))
        return [shell, opts, cmd]

    def terminate(self):
        os.killpg(self._proc.pid, signal.SIGTERM)

    def kill(self):
        os.killpg(self._proc.pid, signal.SIGKILL)


class SbtWindowsProcess(SbtProcess):

    @classmethod
    def _popen(cls, cmdline, **kwargs):
        return subprocess.Popen(cmdline, shell=True, **kwargs)

    def terminate(self):
        self.kill()

    def kill(self):
        cmdline = ['taskkill', '/T', '/F', '/PID', str(self._proc.pid)]
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        subprocess.call(cmdline, startupinfo=si)
