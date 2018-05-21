

from enum import Enum

class AppMode(Enum):
    LAUNCH = 0
    EDIT = 1

class ProcessStatus(Enum):
    STOPPED = 0
    RUNNING = 1

def clearLayout(layout):
    """Deletes the widget in a layout."""
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())
