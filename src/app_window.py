#!/usr/bin/python3

import sys
import os
import json
import logging
from functools import partial

logger = logging.getLogger('process_launcher')
os.environ['QT_API'] = 'pyqt5'

try:
    import qdarkstyle
except Exception:
    logger.log("Exception importing qdarkstyle")
    qdarkstyle = None

try:
    import qdarkgraystyle
except Exception:
    logger.log("Exception importing qdarkgraystyle")
    qdarkgraystyle = None

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QAction, QFileDialog, QMessageBox)

from .configuration import default_config_path, Configuration
from .utils import AppMode, my_path  # , get_plaftorm
from .app_widget import AppWidget




class AppWindow(QMainWindow):
    """docstring for AppWindow"""

    NO_SAVE_FILE = "No file selected"

    def __init__(self, app, profile_filename=None):
        super(AppWindow, self).__init__()
        self.app = app

        self.conf = Configuration(default_config_path)
        self.conf.read()

        self.appWidget = AppWidget(self)
        self.setCentralWidget(self.appWidget)

        self.init_menubar()
        self.select_profile_file(
            profile_filename or self.conf.get("last_profile"))
        if self.selected_profile_path:
            self.load_profile(self.selected_profile_path)

        self.show()

        # Restore the state from the config file
        self.change_theme(self.conf.get("theme"))

        # TODO read this from settings
        # self.setWindowFlags(PyQt5.QtCore.Qt.WindowStaysOnTopHint)

    def select_profile_file(self, filename: str):
        """Changes the current reference to a profile JSON file."""
        self.selected_profile_path = filename
        self.setWindowTitle(self.selected_profile_path or self.NO_SAVE_FILE)

        if self.selected_profile_path:
            self.conf.store("last_profile", self.selected_profile_path)

    def init_menubar(self):
        self.fileMenu = self.menuBar().addMenu("File")
        self.editMenu = self.menuBar().addMenu("Edit")
        self.processesMenu = self.menuBar().addMenu("Processes")
        self.viewMenu = self.menuBar().addMenu("View")

        my_path = os.path.abspath(os.path.dirname(__file__))
        importProcesses = QAction(
            QIcon(os.path.join(my_path, './img/fontawesome/regular/folder-open.svg')), 'Import...', self)
        importProcesses.setShortcut('Ctrl+F')
        importProcesses.setStatusTip('Import processes from a JSON file')
        importProcesses.triggered.connect(self.browse_profile_json)

        self.clearGroups = QAction('Clear groups', self)
        self.clearGroups.triggered.connect(self.appWidget.clear_groups)
        self.clearGroups.setEnabled(False)

        # saveProfile = QAction(QIcon('./imgsave.png'), 'Save', self)
        # saveProfile.setShortcut('Ctrl+S')

        saveAsProfile = QAction(
            QIcon(os.path.join(my_path, './img/fontawesome/regular/save.svg')), 'Save As...', self)
        saveAsProfile.setShortcut('Ctrl+Shift+S')
        saveAsProfile.triggered.connect(self.profile_save_as)

        self.fileMenu.addAction(importProcesses)
        self.fileMenu.addAction(saveAsProfile)

        toggleEditMode = QAction(
            QIcon(os.path.join(my_path, './img/fontawesome/regular/edit.svg')), 'Toggle edit mode', self)
        toggleEditMode.setShortcut('Ctrl+E')
        toggleEditMode.triggered.connect(self.toggle_edit)

        self.editMenu.addAction(toggleEditMode)

        self.groupMenu = self.editMenu.addMenu("Group")
        self.newGroup = self.groupMenu.addMenu("New")
        self.groupMenu.addAction(self.clearGroups)
        self.newEmtpyGroup = QAction('Empty group', self)
        self.newEmtpyGroup.setStatusTip(
            'Create a new empty group to the right of the existing ones')
        self.newEmtpyGroup.setShortcut('Ctrl+N')
        self.newEmtpyGroup.triggered.connect(
            self.appWidget.add_empty_group_right)
        self.newEmtpyGroup.setEnabled(False)

        self.newGroup.addAction(self.newEmtpyGroup)

        minimizeAllProcesses = QAction(
            QIcon(os.path.join(my_path,'./img/fontawesome/regular/window-minimize.svg')), 'Minimize all processes', self)
        minimizeAllProcesses.setShortcut('Ctrl+Down')
        minimizeAllProcesses.triggered.connect(self.minimize_all_processes)
        self.processesMenu.addAction(minimizeAllProcesses)

        restoreAllProcesses = QAction(
            QIcon(os.path.join(my_path, './img/fontawesome/regular/window-maximize.svg')), 'Restore all processes', self)
        restoreAllProcesses.setShortcut('Ctrl+Up')
        restoreAllProcesses.triggered.connect(self.restore_all_processes)
        self.processesMenu.addAction(restoreAllProcesses)

        self.themeMenu = self.viewMenu.addMenu("Theme")

        defaultTheme = QAction('Default', self)
        defaultTheme.triggered.connect(
            partial(self.change_theme, theme_name="default"))
        self.themeMenu.addAction(defaultTheme)
        if qdarkgraystyle:
            darkGrayTheme = QAction('Dark gray', self)
            darkGrayTheme.triggered.connect(
                partial(self.change_theme, theme_name="dark-gray"))
            self.themeMenu.addAction(darkGrayTheme)
        if qdarkstyle:
            darkTheme = QAction('Dark', self)
            darkTheme.triggered.connect(
                partial(self.change_theme, theme_name="dark"))
            self.themeMenu.addAction(darkTheme)

    def load_profile(self, filename: str):
        logger.info("Loading {}".format(filename))
        with open(filename, 'r') as json_data:
            d = json.load(json_data)
            self.appWidget.create_groups_from_dict(d)
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
        string_json = json.dumps(self.appWidget.toJSON(), indent=2)

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
        self.appWidget.toggle_edit()
        mode = self.appWidget.app_mode
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
            self.appWidget.end_all()
            event.accept()
        elif close == QMessageBox.No:
            event.accept()
        else:
            event.ignore()

    def minimize_all_processes(self):
        for group in self.appWidget.group_widgets:
            group.minimize_all_processes()

    def restore_all_processes(self):
        for group in self.appWidget.group_widgets:
            group.restore_all_processes()

    def change_theme(self, theme_name: str):
        if theme_name == "default":
            self.app.setStyleSheet("")
        elif theme_name == "dark-gray":
            self.app.setStyleSheet(qdarkgraystyle.load_stylesheet())
        elif theme_name == "dark":
            self.app.setStyleSheet(
                qdarkstyle.load_stylesheet_from_environment())

        self.conf.store("theme", theme_name)


def main():
    # print(get_platform())
    app = QApplication(sys.argv)

    window = AppWindow(app, sys.argv[1] if len(sys.argv) > 1 else None)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
