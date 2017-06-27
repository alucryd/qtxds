import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from qtxds.main import MainWindow

if __name__ == '__main__':
    application = QApplication(sys.argv)
    window = MainWindow()
    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)
    sys.exit(application.exec_())
