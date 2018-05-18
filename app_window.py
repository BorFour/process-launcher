#!/usr/bin/python3

import sys
import json
import pprint

from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QGridLayout, QWidget, QAction,
                             QFileDialog, QMessageBox)
from PyQt5.QtGui import QIcon
import PyQt5

from process_group import ProcessGroup

N_GROUPS = 2
N_PROCESSES = 4


def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


class AppWidget(QWidget):
    """docstring for AppWidget"""

    def __init__(self, window=None):
        super(AppWidget, self).__init__(window)
        self.n_columns = 3

        self.init_size()
        self.init_layout()

    def clear_groups(self):
        clearLayout(self.widget_layout)
        self.group_widgets = []

    def init_size(self):
        self.setGeometry(300, 300, 900, 900)

    def init_layout(self):
        self.widget_layout = QGridLayout()
        self.setLayout(self.widget_layout)

    def create_groups_from_dict(self, data: dict):
        self.clear_groups()
        for i, group_data in enumerate(data["groups"]):
            process_group = ProcessGroup(self, name=group_data["name"])
            process_group.container.restore_processes(group_data["processes"])
            self.group_widgets.append(process_group)
            self.widget_layout.addWidget(
                process_group, i / self.n_columns,
                i % self.n_columns)

    def toJSON(self) -> dict:
        ret = {}
        ret["groups"] = []
        for group in self.group_widgets:
            ret["groups"].append(group.toJSON())
        pprint.pprint(ret)

        return ret

    def end_all(self):
        for group in self.group_widgets:
            group.container.kill_them_all()
        self.clear_groups()


class AppWindow(QMainWindow):
    """docstring for AppWindow"""

    def __init__(self, profile_filename=None):
        super(AppWindow, self).__init__()
        self.centralWidget = AppWidget(self)
        self.setCentralWidget(self.centralWidget)
        # self.addWidget(self.widget)
        self.init_menubar()
        self.selected_profile_path = profile_filename
        if self.selected_profile_path:
            self.load_profile(self.selected_profile_path)


        self.setWindowTitle(self.selected_profile_path)
        self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)

    def init_menubar(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.viewMenu = self.menuBar().addMenu("View")

        importProcesses = QAction(
            QIcon('img/arrow_restart.png'), 'Import...', self)
        importProcesses.setShortcut('Ctrl+F')
        importProcesses.setStatusTip('Import processes from a JSON file')
        importProcesses.triggered.connect(self.browse_profile_json)

        clearGroups = QAction(
            QIcon('img/arrow_restart.png'), 'Clear groups', self)
        # clearGroups.setShortcut('Ctrl+')

        clearGroups.triggered.connect(self.centralWidget.clear_groups)

        # saveProfile = QAction(QIcon('img/save.png'), 'Save', self)
        # saveProfile.setShortcut('Ctrl+S')

        saveAsProfile = QAction(QIcon('img/save.png'), 'Save As...', self)
        saveAsProfile.setShortcut('Ctrl+Shift+S')
        saveAsProfile.triggered.connect(self.profile_save_as)

        self.fileMenu.addAction(importProcesses)
        # self.fileMenu.addAction(saveProfile)
        self.fileMenu.addAction(saveAsProfile)
        self.fileMenu.addAction(clearGroups)

    def load_profile(self, filename: str):
        print("Loading {}".format(filename))
        with open(filename, 'r') as json_data:
            d = json.load(json_data)
            self.centralWidget.create_groups_from_dict(d)

    def browse_profile_json(self):
        print("browsing")
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(
            self, "Browsing the filesystem for a profile", "", "JSON Files (*.json);;All Files (*)", options=options)
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

        print("Profile succesfully saved to {}".format(filename))

    def select_output_filename(self) -> str or None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Saving profile to a file", "", "JSON Files (*.json)", options=options)
        if file_name:
            print(file_name)
            return file_name
        else:
            return None

    def closeEvent(self, event):
        close = QMessageBox()
        close.setText("Do you want to close running processes?")
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
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
