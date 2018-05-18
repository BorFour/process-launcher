#!/usr/bin/python3

import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtWidgets import QLineEdit, QCompleter, QFileDialog

from process_widget import ProcessWidget


def about_message():
    QMessageBox.about(window, "Title I guess?", "text text text text text text text text text")

def open_file_dialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    file_name, _ = QFileDialog.getOpenFileName(window,"Searching for a file", "","All Files (*);;Python Files (*.py)", options=options)
    if file_name:
        print(file_name)

def open_folder_dialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    # file_name, _ = QFileDialog.getExistingDirectory(window,"Searching for a folder", "","All Files (*)", options=options)
    folder_name = QFileDialog.getExistingDirectory(window,"Searching for a folder","", options)
    if folder_name:
        print(folder_name)

def question_message():
    answer = QMessageBox.question(window, "Title I guess?", "Do you want to open a file?")
    if answer == QMessageBox.Yes:
        open_folder_dialog()
        print("YES")
    elif answer == QMessageBox.No:
        print("NO")

saved_sentences = set(["Old sentence"])
def on_enter():
     print(lineedit.text())
     saved_sentences.add(lineedit.text())
     # completer = QCompleter(saved_sentences)
     # lineedit.setCompleter(completer)
     lineedit.clear()

app = QApplication(sys.argv)

window = QMainWindow()
window.title = "My first window"
window.width = 680
window.height = 520
window.setWindowTitle(window.title)
window.setGeometry(0, 0, window.width, window.height)
window.statusBar().showMessage("Hello")

fileMenu = window.menuBar().addMenu("File")
viewMenu = window.menuBar().addMenu("View")

button = QPushButton("Click me", window)
button.move(200, 200)
button.setToolTip("This is a tooltip")
button.clicked.connect(question_message)

completer = QCompleter(saved_sentences)

lineedit = QLineEdit(window)
lineedit.move(200, 100)
lineedit.resize(280, 30)
lineedit.returnPressed.connect(on_enter)
lineedit.setCompleter(completer)

process_widget = ProcessWidget(window)



window.show()
sys.exit(app.exec())
