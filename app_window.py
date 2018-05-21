#!/usr/bin/python3

import sys
import json
import logging
# import PyQt5
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget, QAction,
                             QFileDialog, QMessageBox)

import utils
from utils import AppMode
from process_group_widget import ProcessGroup, empty_group_data

logger = logging.getLogger('process_launcher')


class AppWidget(QWidget):
    """docstring for AppWidget"""

    def __init__(self, window=None):
        super(AppWidget, self).__init__(window)
        # TODO read this from settings
        self.n_columns = 3

        self.init_size()
        self._init_layout()
        self.clear_groups()
        self.app_mode = AppMode.LAUNCH

    def clear_groups(self):
        """Removes all the widgets in this widget's layout."""
        utils.clearLayout(self.widget_layout)
        self.group_widgets = []

    def init_size(self):
        self.setGeometry(300, 300, 900, 900)

    def _init_layout(self):
        self.widget_layout = QGridLayout()
        self.setLayout(self.widget_layout)

    def adjust_groups_to_layout(self):
        # utils.clearLayout(self.widget_layout)
        for i, process_group in enumerate(self.group_widgets):
            self.widget_layout.addWidget(
                process_group, i / self.n_columns,
                i % self.n_columns)

    def create_groups_from_dict(self, data: dict):
        self.clear_groups()
        for i, group_data in enumerate(data["groups"]):
            self.create_group_from_dict(group_data, i)

    def create_group_from_dict(self, data: dict, index: int):
        process_group = ProcessGroup(self, name=data["name"])
        process_group.container.restore_processes(data["processes"])
        self.group_widgets.append(process_group)
        self.widget_layout.addWidget(
            process_group, index / self.n_columns,
            index % self.n_columns)

        return process_group

    def add_empty_group_right(self):
        """Adds an empty group to the right of the rightmost existing group."""
        return self.create_group_from_dict(empty_group_data, len(self.group_widgets))

    def delete_group(self, group):
        """Deletes a group from the app widget."""
        self.group_widgets.remove(group)
        group.deleteLater()
        self.adjust_groups_to_layout()

    def toJSON(self) -> dict:
        ret = {}
        ret["groups"] = []
        for group in self.group_widgets:
            ret["groups"].append(group.toJSON())
        return ret

    def end_all(self):
        for group in self.group_widgets:
            group.container.kill_them_all()
        self.clear_groups()

    def change_mode(self, mode: AppMode):
        for group in self.group_widgets:
            group.change_mode(mode)

        self.app_mode = mode

    def toggle_edit(self):
        if self.app_mode == AppMode.LAUNCH:
            self.change_mode(AppMode.EDIT)
        elif self.app_mode == AppMode.EDIT:
            self.change_mode(AppMode.LAUNCH)


class AppWindow(QMainWindow):
    """docstring for AppWindow"""

    NO_SAVE_FILE = "No file selected"

    def __init__(self, profile_filename=None):
        super(AppWindow, self).__init__()
        self.centralWidget = AppWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.init_menubar()
        self.select_profile_file(profile_filename)
        if self.selected_profile_path:
            self.load_profile(self.selected_profile_path)

        # TODO read this from settings
        # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)

    def select_profile_file(self, filename: str):
        """Changes the current reference to a profile JSON file."""
        self.selected_profile_path = filename
        self.setWindowTitle(self.selected_profile_path or self.NO_SAVE_FILE)

    def init_menubar(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.editMenu = self.menuBar().addMenu("Edit")
        self.groupMenu = self.menuBar().addMenu("Group")
        self.viewMenu = self.menuBar().addMenu("View")

        importProcesses = QAction(
            QIcon('img/arrow_restart.png'), 'Import...', self)
        importProcesses.setShortcut('Ctrl+F')
        importProcesses.setStatusTip('Import processes from a JSON file')
        importProcesses.triggered.connect(self.browse_profile_json)

        self.clearGroups = QAction('Clear groups', self)
        self.clearGroups.triggered.connect(self.centralWidget.clear_groups)
        self.clearGroups.setEnabled(False)

        # saveProfile = QAction(QIcon('img/save.png'), 'Save', self)
        # saveProfile.setShortcut('Ctrl+S')

        saveAsProfile = QAction(QIcon('img/save.png'), 'Save As...', self)
        saveAsProfile.setShortcut('Ctrl+Shift+S')
        saveAsProfile.triggered.connect(self.profile_save_as)

        self.fileMenu.addAction(importProcesses)
        self.fileMenu.addAction(saveAsProfile)

        toggleEditMode = QAction(
            QIcon('img/edit.png'), 'Toggle edit mode', self)
        toggleEditMode.setShortcut('Ctrl+E')
        toggleEditMode.triggered.connect(self.toggle_edit)

        self.editMenu.addAction(toggleEditMode)

        self.newGroup = self.groupMenu.addMenu("New")
        self.groupMenu.addAction(self.clearGroups)
        self.newEmtpyGroup = QAction('Empty group', self)
        self.newEmtpyGroup.setStatusTip(
            'Create a new empty group to the right of the existing ones')
        self.newEmtpyGroup.setShortcut('Ctrl+N')
        self.newEmtpyGroup.triggered.connect(
            self.centralWidget.add_empty_group_right)
        self.newEmtpyGroup.setEnabled(False)

        self.newGroup.addAction(self.newEmtpyGroup)

    def load_profile(self, filename: str):
        logger.info("Loading {}".format(filename))
        with open(filename, 'r') as json_data:
            d = json.load(json_data)
            self.centralWidget.create_groups_from_dict(d)
        self.select_profile_file(filename)

    def browse_profile_json(self):
        logger.info("Browsing files")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "Browsing the filesystem for a profile", "",
            "JSON Files (*.json);;All Files (*)", options=options)
        if filename:
            self.selected_profile_path = filename
            self.load_profile(self.selected_profile_path)

    def profile_save_as(self):
        filename = self.select_output_filename()
        if not filename:
            # TODO: pop-up
            return
        string_json = json.dumps(self.centralWidget.toJSON(), indent=2)

        with open(filename, "w") as text_file:
            text_file.write(string_json)

        self.select_profile_file(filename)
        print("Profile succesfully saved to {}".format(filename))

    def select_output_filename(self) -> str or None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Saving profile to a file", "",
            "JSON Files (*.json)", options=options)
        if file_name:
            print(file_name)
            return file_name
        else:
            return None

    def change_to_launch(self):
        self.newEmtpyGroup.setEnabled(False)
        self.clearGroups.setEnabled(False)

    def change_to_edit(self):
        self.newEmtpyGroup.setEnabled(True)
        self.clearGroups.setEnabled(True)

    def toggle_edit(self):
        self.centralWidget.toggle_edit()
        mode = self.centralWidget.app_mode
        if mode == AppMode.LAUNCH:
            self.change_to_launch()
        elif mode == AppMode.EDIT:
            self.change_to_edit()

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Do you want to close running processes?")
        close.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        close = close.exec()

        if close == QMessageBox.Yes:
            self.centralWidget.end_all()
            event.accept()
        elif close == QMessageBox.No:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    window = AppWindow(sys.argv[1] if len(sys.argv) > 1 else None)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
