
import PyQt5.QtCore
from PyQt5.QtCore import QSize, QObjectCleanupHandler
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel,
                             QHBoxLayout, QVBoxLayout, QPushButton,
                             QLineEdit, QShortcut)

from process_widget import ProcessWidget
from utils import AppMode

empty_group_data = {
    "name": "",
    "processes": []
}


class ProcessGroup(QWidget):
    """docstring for ProcessGroup"""

    def __init__(self, window=None, name=None, group_number=-1):
        super(ProcessGroup, self).__init__(window)
        self.group_number = group_number
        self.app_mode = window.app_mode
        self.parent_widget = window
        self.container = _ProcessContainer(self)
        self.header = _ProcessGroupHeader(self, name)
        self._init_style()
        self._init_layout()
        self.n_columns = 2

    def add_element(self, element):
        # return
        return self.container.add_element(element)

    def remove_element(self, element):
        return self.container.remove_element(element)

    def _init_style(self):
        pass
        # self.setStyleSheet("margin:5px; border:1px solid rgb(0, 255, 0); ")

    def _init_layout(self):
        self.hbox1 = QHBoxLayout()
        # self.hbox1.setSpacing(1)
        self.hbox1.addWidget(self.header)

        self.hbox2 = QHBoxLayout()
        # self.hbox2.setSpacing(1)
        self.hbox2.addWidget(self.container)

        self.vbox = QVBoxLayout()
        # self.vbox.setStretch(2, 2)
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.setLayout(self.vbox)

    def toJSON(self) -> dict:
        ret = {}
        ret["name"] = self.header.name
        ret["processes"] = []
        for process in self.container.elements:
            ret["processes"].append(process.toJSON())

        return ret

    def change_mode(self, mode: AppMode):
        self.app_mode = mode
        self.header.change_mode(mode)
        self.container.change_mode(mode)

    def update_group_number(self, n):
        self.group_number = n
        self.header.create_shorcut_buttons()

    def add_empty_process(self):
        process_widget = ProcessWidget.create_empty_process(self)
        self.add_element(process_widget)

    def delete(self):
        """Delete this group."""
        self.parent_widget.delete_group(self)


class _ProcessGroupHeader(QWidget):

    def __init__(self, window, name=None):
        super(_ProcessGroupHeader, self).__init__(window)
        self.app_mode = window.app_mode
        self.parent_widget = window

        # This will be overwritten later
        self.title = QLabel(name or 'Group of processes')
        self.title.setAlignment(PyQt5.QtCore.Qt.AlignHCenter)

        self.launch_button = None
        self.stop_button = None
        self.delete_button = None
        self.add_process_button = None
        self.create_variable_widgets(self.app_mode)
        self.create_shorcut_buttons()

        self.widget_layout = None
        self._init_layout()

    @property
    def name(self):
        return self.title.text() if self.title else ""

    def _init_layout(self):
        """
        See:
            https://stackoverflow.com/questions/10416582/replacing-layout-on-a-qwidget-with-another-layout?lq=1
        """
        if self.layout():
            QObjectCleanupHandler().add(self.layout())

        self.widget_layout = QVBoxLayout()
        self.title_and_delete_layout = QHBoxLayout()
        self.title_and_delete_layout.addWidget(self.title)
        if self.delete_button:
            self.title_and_delete_layout.addWidget(self.delete_button)
        if self.add_process_button:
            self.title_and_delete_layout.addWidget(self.add_process_button)
        self.widget_layout.addLayout(self.title_and_delete_layout)
        self.widget_layout.addWidget(self.launch_button)
        self.widget_layout.addWidget(self.stop_button)
        self.setLayout(self.widget_layout)

    def safe_delete(self, widgets):
        for widget in widgets:
            if widget:
                widget.deleteLater()

    def create_variable_widgets(self, mode):
        self.safe_delete([self.delete_button, self.add_process_button])

        if mode == AppMode.LAUNCH:
            self.delete_button = None
            self.add_process_button = None

            old_title = self.title
            self.title = QLabel(self.name)
            self.title.setAlignment(PyQt5.QtCore.Qt.AlignHCenter)
            old_title.deleteLater()
        elif mode == AppMode.EDIT:
            old_title = self.title
            self.title = QLineEdit(self.name)
            old_title.deleteLater()

            self.delete_button = QPushButton(self)
            self.delete_button.setIcon(QIcon('./img/trash.png'))
            self.delete_button.setIconSize(QSize(24, 24))
            self.delete_button.clicked.connect(self.parent_widget.delete)

            self.add_process_button = QPushButton(self)
            self.add_process_button.setIcon(QIcon('./img/plus.png'))
            self.add_process_button.setIconSize(QSize(24, 24))
            self.add_process_button.clicked.connect(
                self.parent_widget.add_empty_process)

    def create_shorcut_buttons(self):
        self.safe_delete([self.launch_button, self.stop_button])

        # These buttons need to be created again when other groups are deleted,
        # in order to update the shortcut
        self.launch_button = QPushButton(self)
        self.launch_button.setText("Launch all")
        self.launch_button.clicked.connect(
            self.parent_widget.container.run_all)

        alt_num_action = QShortcut('Alt+{}'.format(self.parent_widget.group_number+1), self.launch_button)
        alt_num_action.activated.connect(self.launch_button.click)

        self.stop_button = QPushButton(self)
        self.stop_button.setText("Stop this group's processes")
        self.stop_button.clicked.connect(
            self.parent_widget.container.kill_them_all)

        alt_shift_num_action = QShortcut('Alt+Shift+{}'.format(self.parent_widget.group_number+1), self.stop_button)
        alt_shift_num_action.activated.connect(self.stop_button.click)

    def change_to_launch(self):
        self.create_variable_widgets(self.app_mode)
        self._init_layout()

    def change_to_edit(self):
        self.create_variable_widgets(self.app_mode)
        self._init_layout()

    def change_mode(self, mode: AppMode):
        self.app_mode = mode
        if mode == AppMode.LAUNCH:
            self.change_to_launch()
        elif mode == AppMode.EDIT:
            self.change_to_edit()


class _ProcessContainer(QWidget):

    def __init__(self, parent):
        super(_ProcessContainer, self).__init__(parent)
        self.app_mode = parent.app_mode
        self.parent_widget = parent
        self._init_layout()
        self.elements = set()

    def _init_layout(self):
        self.widget_layout = QGridLayout()
        self.setLayout(self.widget_layout)

    def adjust_processes_to_layout(self):
        for i, element in enumerate(self.elements):
            self.widget_layout.addWidget(element, i / self.parent_widget.n_columns,
                                         i % self.parent_widget.n_columns)

    def add_element(self, element):
        self.widget_layout.addWidget(element, len(self.elements) / self.parent_widget.n_columns,
                                     len(self.elements) % self.parent_widget.n_columns)
        self.elements.add(element)

    def remove_element(self, element):
        self.elements.remove(element)
        element.deleteLater()
        self.adjust_processes_to_layout()

    def run_all(self):
        for process_widget in self.elements:
            process_widget.process.restart()  # REVIEW: or run?

    def kill_them_all(self):
        for process_widget in self.elements:
            process_widget.process.kill()  # REVIEW: or terminate?

    def restore_processes(self, data: list):
        """Data is normally a list in the JSON format."""
        for d in data:
            p = ProcessWidget(self, d["args"], directory=d["dir"])
            self.add_element(p)

    def change_mode(self, mode: AppMode):
        self.app_mode = mode
        for process in self.elements:
            process.change_mode(mode)
