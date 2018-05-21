
import subprocess

from PyQt5.QtCore import QSize, QObjectCleanupHandler
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QLineEdit, QAbstractItemView,
    QMenu)

from utils import AppMode, ProcessStatus

DEFAULT_DIRECTORY = "~/"

empty_process_data = {
    "name": "empty process",
    "dir": DEFAULT_DIRECTORY,
    "args": [
        " "
    ],
    "description": "This is an empty process template"
}


class PopenProcess(object):
    """docstring for PopenProcess"""

    def __init__(self, args_table_widget: QTableWidget, name=None, directory_widget=None):
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
        raise NotImplementedError("Method 'run' not implemented")

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


class KonsoleProcess(PopenProcess):
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


class ProcessWidget(QWidget):
    """docstring for ProcessWidget"""
    n_processes = 0

    @classmethod
    def create_empty_process(cls, window):
        d = empty_process_data
        return cls(window, *d["args"], directory=d["dir"], name=d["name"])

    def __init__(self, window, *args, directory=None, name=None):
        super(ProcessWidget, self).__init__(window)
        self.app_mode = window.app_mode
        self.args = list(*args)
        self.parent_widget = window
        self._init_args_table(self.args)

        self.directory_widget = QLabel(directory)
        self.process = KonsoleProcess(self.args_table_widget,
                                      name=name or "process {}".format(
                                          ProcessWidget.n_processes), directory_widget=self.directory_widget or DEFAULT_DIRECTORY)

        self.restart_button = QPushButton(self)
        self.restart_button.setIcon(QIcon('./img/arrow_restart.png'))
        self.restart_button.setIconSize(QSize(24, 24))
        self.restart_button.clicked.connect(self.process.restart)

        self.close_button = None
        self.create_variable_widgets(self.app_mode)

        ProcessWidget.n_processes += 1
        self._init_layout()

    def create_variable_widgets(self, mode):
        if self.close_button:
            self.close_button.deleteLater()

        if mode == AppMode.EDIT:
            self.close_button = QPushButton(self)
            self.close_button.setIcon(QIcon('./img/close.png'))
            self.close_button.setIconSize(QSize(24, 24))
            self.close_button.clicked.connect(self.close)
        else:
            self.close_button = None

    def _init_args_table(self, *args):
        self.args_table_widget = QTableWidget()
        self.args_table_widget.setRowCount(0)
        self.args_table_widget.setColumnCount(1)
        for i, arg in enumerate(*args):
            self.args_table_widget.insertRow(i)
            self.args_table_widget.setItem(0, i, QTableWidgetItem(arg))

    def _init_layout(self):
        if self.layout():
            QObjectCleanupHandler().add(self.layout())

        self.hbox1 = QHBoxLayout()
        self.hbox1.addWidget(self.directory_widget)
        if self.close_button:
            self.hbox1.addWidget(self.close_button)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.args_table_widget)

        self.hbox3 = QHBoxLayout()
        self.hbox3.addWidget(self.restart_button)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.setLayout(self.vbox)

    def contextMenuEvent(self, event):
        n_items = len(self.args_table_widget.selectedItems())

        if n_items == 0:
            return

        context_menu = QMenu(self)
        addNewRowBefore = context_menu.addAction("Add cell before")
        addNewRowAfter = context_menu.addAction("Add cell after")
        deleteRow = context_menu.addAction(
            "Delete cells" if n_items > 1 else "Delete cell")

        if self.app_mode == AppMode.LAUNCH:
            addNewRowBefore.setEnabled(False)
            addNewRowAfter.setEnabled(False)
            deleteRow.setEnabled(False)
        elif self.app_mode == AppMode.EDIT:
            addNewRowBefore.setEnabled(True)
            addNewRowAfter.setEnabled(True)
            deleteRow.setEnabled(True)

        mousePositionAtEvent = event.pos()
        action = context_menu.exec_(self.mapToGlobal(mousePositionAtEvent))

        if action == addNewRowBefore:
            first_item = self.args_table_widget.selectedItems()[0]
            self.add_new_arg(pos=first_item.row())
        elif action == addNewRowAfter:
            last_item = self.args_table_widget.selectedItems()[-1]
            self.add_new_arg(pos=last_item.row() + 1)
        elif action == deleteRow:
            for item in self.args_table_widget.selectedItems():
                self.args_table_widget.removeRow(item.row())

    def add_new_arg(self, arg=None, pos=None):
        arg = arg or " "
        pos = QTableWidget().rowCount() if pos is None else pos
        self.args_table_widget.insertRow(pos)
        self.args_table_widget.setItem(0, pos, QTableWidgetItem(arg))

    def close(self):
        self.parent_widget.remove_element(self)

    def update_process_references(self):
        self.process.directory_widget = self.directory_widget
        self.process.args_table_widget = self.args_table_widget

    def change_to_launch(self):
        old_directory = self.directory_widget
        self.directory_widget = QLabel(old_directory.text())
        old_directory.deleteLater()
        self.args_table_widget.setEditTriggers(
            QAbstractItemView.NoEditTriggers)

        self.create_variable_widgets(self.app_mode)

        self._init_layout()

    def change_to_edit(self):
        old_directory = self.directory_widget
        self.directory_widget = QLineEdit(old_directory.text())
        self.directory_widget.setPlaceholderText("Current workdir")
        old_directory.deleteLater()
        self.args_table_widget.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

        self.create_variable_widgets(self.app_mode)

        self._init_layout()

    def change_mode(self, mode: AppMode):
        self.app_mode = mode
        if mode == AppMode.LAUNCH:
            self.change_to_launch()
        elif mode == AppMode.EDIT:
            self.change_to_edit()
        self.update_process_references()

    def toJSON(self) -> dict:
        ret = {}
        ret["dir"] = self.process.directory
        ret["args"] = []

        for arg in self.process.args:
            ret["args"].append(arg)

        return ret
