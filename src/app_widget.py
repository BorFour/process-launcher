from PyQt5.QtWidgets import (QGridLayout, QWidget)

from . import utils
from .utils import AppMode
from .process_group_widget import ProcessGroup, empty_group_data

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
            process_group.group_number = i
            self.widget_layout.addWidget(
                process_group, i / self.n_columns,
                i % self.n_columns)

    def create_groups_from_dict(self, data: dict):
        self.clear_groups()
        for i, group_data in enumerate(data["groups"]):
            self.create_group_from_dict(group_data, i)

    def create_group_from_dict(self, data: dict, index: int):
        process_group = ProcessGroup(self, name=data["name"], group_number=len(self.group_widgets))
        process_group.container.restore_processes(data["processes"])
        self.group_widgets.append(process_group)
        self.widget_layout.addWidget(
            process_group, index / self.n_columns,
            index % self.n_columns)

        return process_group

    def add_empty_group_right(self):
        """Adds an empty group to the right of the rightmost existing group."""
        new_group = self.create_group_from_dict(empty_group_data, len(self.group_widgets))
        for n, group in enumerate(self.group_widgets):
            group.update_group_number(n)

        return new_group

    def delete_group(self, group):
        """Deletes a group from the app widget."""
        self.group_widgets.remove(group)
        group.deleteLater()
        self.adjust_groups_to_layout()
        for n, group in enumerate(self.group_widgets):
            group.update_group_number(n)

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
