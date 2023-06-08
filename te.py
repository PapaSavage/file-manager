from PyQt5.QtWidgets import (
    QDialog,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QApplication,
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


class ProgressThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(101):
            self.update_progress.emit(i)
            self.msleep(100)  # Имитация работы


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Прогресс")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        self.progress_thread = ProgressThread()
        self.progress_thread.update_progress.connect(self.update_progress)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_ui(self):
        if self.progress_bar.value() == 100:
            self.cancel_button.setEnabled(False)
            self.timer.stop()

    def start_progress(self):
        self.progress_thread.start()
        self.cancel_button.setEnabled(True)

    def cancel(self):
        self.progress_thread.terminate()
        self.cancel_button.setEnabled(False)
        self.progress_bar.reset()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    main_window = QDialog()
    main_window.setWindowTitle("Главное окно")
    main_window.setGeometry(100, 100, 300, 200)

    button = QPushButton("Запустить прогресс")
    progress_dialog = ProgressDialog()

    def show_progress_dialog():
        progress_dialog.start_progress()
        progress_dialog.exec_()

    button.clicked.connect(show_progress_dialog)

    layout = QVBoxLayout()
    layout.addWidget(button)
    main_window.setLayout(layout)

    main_window.show()
    sys.exit(app.exec_())
