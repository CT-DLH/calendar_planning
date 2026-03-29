# 主入口文件
import sys
from PyQt6.QtWidgets import QApplication
from src.ui import ScheduleWindow

def main():
    app = QApplication(sys.argv)
    window = ScheduleWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
