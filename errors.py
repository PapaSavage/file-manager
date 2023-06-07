import PyQt5
from PyQt5.QtWidgets import QMessageBox


# class Errors():
def itemnotExist(self):
    dlg = QMessageBox()
    dlg.setWindowTitle("Ошибка")
    dlg.setText("Файла для копирования не существует")
    button = dlg.exec()
