import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QPushButton, QWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPalette, QColor
from whistle_detector import WhistleDetector


class WhistleApp(QMainWindow):
    detected_signal = Signal(bool)  # Сигнал для обновления статуса

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whistle Detector")
        self.setGeometry(100, 100, 500, 300)
        self.detector = WhistleDetector()
        self.listening_thread = None
        self.is_dark_theme = False

        self.init_ui()
        self.update_device_list()
        self.detected_signal.connect(self.update_status)

    def init_ui(self):
        # Основной виджет и макет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.layout = QVBoxLayout(main_widget)

        # Заголовок
        self.title_label = QLabel("Whistle Detector", alignment=Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Выбор устройства
        self.device_layout = QHBoxLayout()
        self.device_label = QLabel("Input Device:")
        self.device_dropdown = QComboBox()
        self.device_layout.addWidget(self.device_label)
        self.device_layout.addWidget(self.device_dropdown)
        self.layout.addLayout(self.device_layout)

        # Кнопки управления
        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Listening")
        self.stop_button = QPushButton("Stop Listening")
        self.stop_button.setEnabled(False)
        self.theme_button = QPushButton("Switch to Dark Theme")
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.button_layout.addWidget(self.theme_button)
        self.layout.addLayout(self.button_layout)

        # Статус
        self.status_label = QLabel("Status: Idle", alignment=Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: gray;")
        self.layout.addWidget(self.status_label)

        # Автор
        self.author_label = QLabel(
            '<a href="https://github.com/nntdgrss">@nntdgrss</a>',
            alignment=Qt.AlignCenter
        )
        self.author_label.setOpenExternalLinks(True)
        self.author_label.setStyleSheet("font-size: 12px; color: blue;")
        self.layout.addWidget(self.author_label)

        # События кнопок
        self.start_button.clicked.connect(self.start_listening)
        self.stop_button.clicked.connect(self.stop_listening)
        self.theme_button.clicked.connect(self.toggle_theme)

    def update_device_list(self):
        devices = self.detector.list_input_devices()
        self.device_dropdown.clear()
        self.device_dropdown.addItems(devices)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        palette = QPalette()
        if self.is_dark_theme:
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(15, 15, 15))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            self.theme_button.setText("Switch to Light Theme")
        else:
            palette = QApplication.style().standardPalette()
            self.theme_button.setText("Switch to Dark Theme")
        self.setPalette(palette)

    def start_listening(self):
        selected_device = self.device_dropdown.currentIndex()
        if selected_device == -1:
            self.status_label.setText("Status: No device selected")
            return
        self.detector.set_input_device(selected_device)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Status: Listening...")
        self.listening_thread = threading.Thread(target=self.detector.start_listening,
                                                 args=(self.detected_signal.emit,))
        self.listening_thread.start()

    def stop_listening(self):
        self.detector.stop_listening()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Status: Idle")

    @Slot(bool)
    def update_status(self, detected):
        if detected:
            self.status_label.setText("Status: Whistle Detected!")
        else:
            self.status_label.setText("Status: Listening...")

    def closeEvent(self, event):
        if self.listening_thread and self.listening_thread.is_alive():
            self.detector.stop_listening()
            self.listening_thread.join()
        self.detector.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhistleApp()
    window.show()
    sys.exit(app.exec())
