import asyncio
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QToolBar,
                             QVBoxLayout, QWidget, QDesktopWidget, QGridLayout, QGroupBox)
from quamash import QEventLoop

from qtxds.roms import NdsRom
from tools import NdsTools, ThreedsTools


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

        self.nds_main_grid()
        self.setCentralWidget(self.nds_group_box)

        self.menu_bar = self.menuBar()
        self.about_dialog = AboutDialog()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        self.file_menu()
        self.help_menu()

        self.tool_bar_items()

        self.rom = None
        self.ndstools = NdsTools(self.status_bar)
        self.threedstools = ThreedsTools(self.status_bar)

        filters = []
        if self.ndstools.path:
            filters.append('Nintendo DS ROMs (*.nds)')
        if self.threedstools.path:
            filters.append('Nintendo 3DS ROMs (*.3ds)')
        if self.ndstools.path or self.threedstools.path:
            self.filters = ';;'.join(filters)

    def nds_main_grid(self):
        self.nds_group_box = QGroupBox("NDS")

        layout = QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)

        self.rom_title = QLabel()
        self.rom_game_code = QLabel()
        self.rom_maker_code = QLabel()

        layout.addWidget(QLabel("Title"), 0, 0)
        layout.addWidget(self.rom_title, 0, 1)
        layout.addWidget(QLabel("Game Code"), 1, 0)
        layout.addWidget(self.rom_game_code, 1, 1)
        layout.addWidget(QLabel("Maker Code"), 2, 0)
        layout.addWidget(self.rom_maker_code, 2, 1)

        self.nds_group_box.setLayout(layout)

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
        self.tool_bar_fix_header_crc_action = QAction('Fix Header CRC', self)
        self.tool_bar_fix_header_crc_action.triggered.connect(self.fix_header_crc)
        self.tool_bar_fix_header_crc_action.setEnabled(False)

        self.tool_bar_decrypt_action = QAction('Decrypt', self)
        self.tool_bar_decrypt_action.triggered.connect(self.decrypt)
        self.tool_bar_decrypt_action.setEnabled(False)

        self.tool_bar_encrypt_nintendo_action = QAction('Encrypt (Nintendo)', self)
        self.tool_bar_encrypt_nintendo_action.triggered.connect(self.encrypt_nintendo)
        self.tool_bar_encrypt_nintendo_action.setEnabled(False)

        self.tool_bar_encrypt_others_action = QAction('Encrypt (others)', self)
        self.tool_bar_encrypt_others_action.triggered.connect(self.encrypt_others)
        self.tool_bar_encrypt_others_action.setEnabled(False)

        self.tool_bar_extract_action = QAction('Extract', self)
        self.tool_bar_extract_action.triggered.connect(self.extract)
        self.tool_bar_extract_action.setEnabled(False)

        self.tool_bar_rebuild_action = QAction('Rebuild', self)
        self.tool_bar_rebuild_action.triggered.connect(self.rebuild)
        self.tool_bar_rebuild_action.setEnabled(False)

        self.tool_bar.addAction(self.tool_bar_fix_header_crc_action)
        self.tool_bar.addAction(self.tool_bar_decrypt_action)
        self.tool_bar.addAction(self.tool_bar_encrypt_nintendo_action)
        self.tool_bar.addAction(self.tool_bar_encrypt_others_action)
        self.tool_bar.addAction(self.tool_bar_extract_action)
        self.tool_bar.addAction(self.tool_bar_rebuild_action)

    def open_nds_rom_callback(self, future):
        """Enables the extract QAction."""
        if not future.exception():
            self.rom_title.setText(self.rom.title)
            self.rom_game_code.setText(self.rom.game_code)
            self.rom_maker_code.setText(self.rom.maker_code)
            self.tool_bar_extract_action.setEnabled(True)

    def enable_rebuild_action(self, future):
        """Enables the extract QAction."""
        if not future.exception():
            self.tool_bar_rebuild_action.setEnabled(True)

    def open_file(self):
        """Open a QFileDialog to allow the user to open a file into the application."""
        filename, accepted = QFileDialog().getOpenFileName(self, 'Open File', str(Path.home()), self.filters)

        if accepted:
            path = Path(filename)
            if path.suffix == '.nds':
                self.rom = NdsRom(path)
            if self.rom:
                coro = self.ndstools.info(self.rom)
                future = asyncio.ensure_future(coro)
                future.add_done_callback(self.open_nds_rom_callback)

    def fix_header_crc(self):
        """Fix the open ROM's header's CRC."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.fix_header_crc(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_action)

    def decrypt(self):
        """Decrypt the open ROM."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.decrypt(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_action)

    def encrypt_nintendo(self):
        """Encrypt the open ROM (Nintendo)."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.encrypt_nintendo(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_action)

    def encrypt_others(self):
        """Encrypt the open ROM (Others)."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.encrypt_others(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_action)

    def extract(self):
        """Extract the open ROM."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.extract(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_action)

    def rebuild(self):
        """Rebuild the open ROM."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.rebuild(self.rom)
            asyncio.ensure_future(coro)


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

if __name__ == '__main__':
    sys._excepthook = sys.excepthook

    def excepthook(excepttype, value, traceback):
        print(excepttype, value, traceback)
        sys._excepthook(excepttype, value, traceback)
        sys.exit(1)

    sys.excepthook = excepthook

    application = QApplication(sys.argv)
    loop = QEventLoop(application)
    loop.set_debug(True)
    # executor = QThreadExecutor(1)
    # loop.set_default_executor(executor)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)

    with loop:
        loop.run_forever()


