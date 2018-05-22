
import subprocess

from utils import ProcessStatus, kill_command_windows, get_platform, SupportedPlatforms


class PopenProcess(object):
    """docstring for PopenProcess"""

    def __init__(self, args_table_widget, name=None, directory_widget=None):
        super(PopenProcess, self).__init__()
        self.args_table_widget = args_table_widget
        self.name = name
        self.directory_widget = directory_widget
        self.popen = None

    @property
    def status(self) -> ProcessStatus:
        if not self.popen or self.popen:
            return ProcessStatus.STOPPED
        return_code = self.popen.poll()
        if not return_code:
            return ProcessStatus.RUNNING
        # TODO: switch the values of return_code (POSIX only)
        else:
            return ProcessStatus.STOPPED

    @property
    def args(self) -> list:
        return [
            self.args_table_widget.item(i, 0).text()
            for i in range(self.args_table_widget.rowCount())
            if self.args_table_widget.item(i, 0)
        ]

    @property
    def directory(self) -> str:
        return self.directory_widget.text()

    def restart(self):
        if self.popen:
            self.kill()
        self.run()

    def run(self):
        raise NotImplementedError("Method not implemented")

    def kill(self):
        if self.popen:
            self.popen.kill()

    def terminate(self):
        if self.popen:
            self.popen.terminate()
        self.popen = None

    def transform_to(self, cls):
        """Transform this process into an instance of another class."""
        return cls(args_table_widget=self.args_table_widget,
                   name=self.name,
                   directory_widget=self.directory_widget)


class LinuxProcess(PopenProcess):
    pass


class WindowsProcess(PopenProcess):
    def kill(self):
        """self.popen.kill doesn't work on Windows."""
        if self.popen:
            kill_command_windows(self.popen.pid)


class KonsoleProcess(LinuxProcess):
    def create_command(self) -> str:
        command = "{}".format(self.args[0])
        for argument in self.args[1:]:
            command += " {}".format(argument)
        return command

    def run(self):
        self.popen = subprocess.Popen(args=[
            'konsole',
            '--workdir', self.directory,
            # Run the new instance of Konsole in a separate process.
            '--noclose',
            # '--separate',
            '-e', '{}'.format(self.create_command())
        ], shell=False)


class CustomWindowsProcess(WindowsProcess):
    def run(self):
        self.popen = subprocess.Popen(args=[
            *self.args
        ], shell=True)


CurrentPlatformProcess = KonsoleProcess if get_platform(
) == SupportedPlatforms.LINUX else CustomWindowsProcess
"""Depending on the platform, a default process is selected."""
