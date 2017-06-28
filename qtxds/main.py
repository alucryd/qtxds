import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pkg_resources
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QToolBar,
                             QVBoxLayout, QWidget)

from qtxds.roms import NdsRom
from tools import NdsTools


class MainWindow(QMainWindow):
    """Create the main window that stores all of the widgets necessary for the application."""

    def __init__(self, parent=None):
        """Initialize the components of the main window."""
        super(MainWindow, self).__init__(parent)
        self.resize(640, 480)
        self.setWindowTitle('qtxds')
        # window_icon = pkg_resources.resource_filename('qtxds.images',
        #                                               'ic_insert_drive_file_black_48dp_1x.png')
        # self.setWindowIcon(QIcon(window_icon))

        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)

        self.menu_bar = self.menuBar()
        self.about_dialog = AboutDialog()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        self.file_menu()
        self.help_menu()

        self.tool_bar_items()

        self.rom = None
        self.ndstools = NdsTools(self.status_bar)

        # Asyncio Event Loop
        if sys.platform == "win32":
            self.loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(self.loop)
        else:
            self.loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        self.loop.set_default_executor(executor)


    def file_menu(self):
        """Create a file submenu with an Open File item that opens a file dialog."""
        self.file_sub_menu = self.menu_bar.addMenu('File')

        self.open_action = QAction('Open File', self)
        self.open_action.setStatusTip('Open a file into qtxds.')
        self.open_action.setShortcut('CTRL+O')
        self.open_action.triggered.connect(self.open_file)

        self.exit_action = QAction('Exit Application', self)
        self.exit_action.setStatusTip('Exit the application.')
        self.exit_action.setShortcut('CTRL+Q')
        self.exit_action.triggered.connect(lambda: QApplication.quit())

        self.file_sub_menu.addAction(self.open_action)
        self.file_sub_menu.addAction(self.exit_action)

    def help_menu(self):
        """Create a help submenu with an About item tha opens an about dialog."""
        self.help_sub_menu = self.menu_bar.addMenu('Help')

        self.about_action = QAction('About', self)
        self.about_action.setStatusTip('About the application.')
        self.about_action.setShortcut('CTRL+H')
        self.about_action.triggered.connect(lambda: self.about_dialog.exec_())

        self.help_sub_menu.addAction(self.about_action)

    def tool_bar_items(self):
        """Create a tool bar for the main window."""
        self.tool_bar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)
        self.tool_bar.setMovable(False)

        # open_icon = pkg_resources.resource_filename('qtxds.images',
        #                                             'ic_open_in_new_black_48dp_1x.png')
        tool_bar_extract_action = QAction('Extract', self)
        tool_bar_extract_action.triggered.connect(self.extract)

        tool_bar_extract_banner_bmp_action = QAction('Extract Banner BMP', self)
        tool_bar_extract_banner_bmp_action.triggered.connect(self.extract_banner_bmp)

        self.tool_bar.addAction(tool_bar_extract_action)
        self.tool_bar.addAction(tool_bar_extract_banner_bmp_action)

    def open_file(self):
        """Open a QFileDialog to allow the user to open a file into the application."""
        filters = 'Nintendo DS ROMs (*.nds);;Nintendo 3DS ROMs (*.3ds)'
        filename, accepted = QFileDialog().getOpenFileName(self, 'Open File', str(Path.home()), filters)

        if accepted:
            path = Path(filename)
            if path.suffix == '.nds':
                self.rom = NdsRom(path)
            if self.rom:
                self.loop.run_until_complete(self.ndstools.info(self.rom))
                print(self.rom.title)
                print(self.rom.code)
                print(self.rom.maker)

    def extract(self):
        """Extract the open ROM."""
        if isinstance(self.rom, NdsRom):
            self.loop.run_in_executor(None, self.ndstools.extract, self.rom)

    def extract_banner_bmp(self):
        """Extract the open ROM's BMP banner."""
        if isinstance(self.rom, NdsRom):
            self.loop.run_until_complete(self.ndstools.extract_banner_bmp(self.rom))


class AboutDialog(QDialog):
    """Create the necessary elements to show helpful text in a dialog."""

    def __init__(self, parent=None):
        """Display a dialog that shows application information."""
        super(AboutDialog, self).__init__(parent)

        self.setWindowTitle('About')
        # help_icon = pkg_resources.resource_filename('qtxds.images',
        #                                             'ic_help_black_48dp_1x.png')
        # self.setWindowIcon(QIcon(help_icon))
        self.resize(300, 200)

        author = QLabel('Maxime Gauduin')
        author.setAlignment(Qt.AlignCenter)

        github = QLabel('GitHub: alucryd')
        github.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignVCenter)

        self.layout.addWidget(author)
        self.layout.addWidget(github)

        self.setLayout(self.layout)
