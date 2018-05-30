
from PyQt5.QtCore import QSize, QObjectCleanupHandler
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QLineEdit, QAbstractItemView,
    QMenu)

from .utils import AppMode, browse_existing_directory, parse_dropped_file
from .process import CurrentPlatformProcess

DEFAULT_DIRECTORY = "~/"

empty_process_data = {
    "name": "empty process",
    "dir": DEFAULT_DIRECTORY,
    "args": [
        " "
    ],
    "description": "This is an empty process template"
}


class ProcessWidget(QWidget):
    """docstring for ProcessWidget"""
    n_processes = 0

    @classmethod
    def create_empty_process(cls, window):
        d = empty_process_data
        return cls(window, *d["args"], directory=d["dir"], name=d["name"])

    def __init__(self, window, *args, directory=None, name=None):
        super(ProcessWidget, self).__init__(window)
        self.setAcceptDrops(True)
        self.app_mode = window.app_mode
        self.args = list(*args)
        self.parent_widget = window
        self._init_args_table(self.args)

        self.directory_widget = QLabel(directory)
        self.process = CurrentPlatformProcess(self.args_table_widget,
                                              name=name or "process {}".format(
                                                  ProcessWidget.n_processes), directory_widget=self.directory_widget or DEFAULT_DIRECTORY)

        self.restart_button = QPushButton(self)
        self.restart_button.setIcon(QIcon('./img/arrow_restart.png'))
        self.restart_button.setIconSize(QSize(24, 24))
        self.restart_button.clicked.connect(self.relaunch_process)

        self.close_button = None
        self.browse_folder_button = None
        self.process_id_label = None
        self.create_variable_widgets(self.app_mode)

        ProcessWidget.n_processes += 1
        self._init_layout()

    def create_variable_widgets(self, mode):

        if self.directory_widget:
            directory_name = self.directory_widget.text()
            self.directory_widget.deleteLater()

        if self.process_id_label:
            self.process_id_label.deleteLater()

        if self.close_button:
            self.close_button.deleteLater()

        if self.browse_folder_button:
            self.browse_folder_button.deleteLater()

        self.process_id_label = QLabel(
            self.process.pid if self.process.pid else "stopped")

        if mode == AppMode.EDIT:
            self.directory_widget = QLineEdit(directory_name)
            self.directory_widget.setPlaceholderText("Current workdir")

            self.close_button = QPushButton(self)
            self.close_button.setIcon(QIcon('./img/close.png'))
            self.close_button.setIconSize(QSize(24, 24))
            self.close_button.clicked.connect(self.close)

            self.browse_folder_button = QPushButton(self)
            self.browse_folder_button.setIcon(QIcon('./img/folder_browse.png'))
            self.browse_folder_button.setIconSize(QSize(24, 24))
            self.browse_folder_button.clicked.connect(
                self.browse_directory_name)

        else:

            self.directory_widget = QLabel(directory_name)

            self.close_button = None
            self.browse_folder_button = None

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
        self.hbox1.addWidget(self.process_id_label)
        if self.browse_folder_button:
            self.hbox1.addWidget(self.browse_folder_button)

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

    def dragEnterEvent(self, event):
        # TODO accept only .exe files
        # event.mimeData().hasFormat('text/plain')
        event.accept()

    def dropEvent(self, event):
        # TODO accept only .exe files
        # event.mimeData().hasFormat('text/plain')
        text = event.mimeData().text()
        print(text)
        text = parse_dropped_file(text)
        self.add_new_arg(arg=text, pos=0)

    def browse_directory_name(self):
        filename = browse_existing_directory(self, "Select a folder")
        if filename:
            print(filename)
            self.directory_widget.setText(filename)

    def add_new_arg(self, arg=None, pos=None):
        arg = arg or " "
        pos = QTableWidget().rowCount() if pos is None else pos
        self.args_table_widget.insertRow(pos)
        self.args_table_widget.setItem(0, pos, QTableWidgetItem(arg))

    def close(self):
        self.parent_widget.remove_element(self)

    def relaunch_process(self):
        self.process.restart()
        print(self.process.pid)
        print(self.process_id_label)
        print('Window id: {}'.format(self.process.window_id))
        if self.process_id_label:
            self.process_id_label.setText("PID: {}".format(self.process.pid))

    def update_process_references(self):
        self.process.directory_widget = self.directory_widget
        self.process.args_table_widget = self.args_table_widget

    def change_to_launch(self):

        self.args_table_widget.setEditTriggers(
            QAbstractItemView.NoEditTriggers)

        self.create_variable_widgets(self.app_mode)

        self._init_layout()

    def change_to_edit(self):
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
