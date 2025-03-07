import sys
from lib.ui.main_window import Main_Screen
from PySide6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voronoi Diagram Basics")

        self.main_widget = Main_Screen()
        self.setCentralWidget(self.main_widget)

        self.setGeometry(100, 100, 800, 600)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
