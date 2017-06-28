import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from qtxds.main import MainWindow

if __name__ == '__main__':
    sys._excepthook = sys.excepthook

    def excepthook(excepttype, value, traceback):
        print(excepttype, value, traceback)
        sys._excepthook(excepttype, value, traceback)
        sys.exit(1)

    sys.excepthook = excepthook

    application = QApplication(sys.argv)
    window = MainWindow()
    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)
    sys.exit(application.exec_())
