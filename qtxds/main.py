import asyncio
import sys
from pathlib import Path

import humanize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QToolBar,
                             QVBoxLayout, QDesktopWidget, QGridLayout, QGroupBox, QLineEdit)
from quamash import QEventLoop

from qtxds.roms import NdsRom
from tools import NdsTools, ThreedsTools


class MainWindow(QMainWindow):
    """Create the main window that stores all of the widgets necessary for the application."""

    def __init__(self, parent=None):
        """Initialize the components of the main window."""
        super(MainWindow, self).__init__(parent)
        # self.resize(640, 480)
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

        hbox_layout = QHBoxLayout()

        info_group_box = QGroupBox('General Information')
        content_group_box = QGroupBox('Content')

        info_grid_layout = QGridLayout()
        content_grid_layout = QGridLayout()

        self.rom_title = QLineEdit()
        self.rom_game_code = QLineEdit()
        self.rom_maker_code = QLineEdit()
        self.rom_secure_area_crc = QLabel()
        self.rom_decrypted = QLabel()
        self.rom_header_crc = QLabel()
        self.rom_size = QLabel()

        self.rom_arm9_size = QLabel()
        self.rom_arm7_size = QLabel()
        self.rom_overlay9_size = QLabel()
        self.rom_overlay7_size = QLabel()
        self.rom_data_size = QLabel()
        self.rom_overlay_size = QLabel()
        self.rom_banner_size = QLabel()
        self.rom_header_size = QLabel()

        info_grid_layout.addWidget(QLabel('Title'), 0, 0)
        info_grid_layout.addWidget(self.rom_title, 0, 1)
        info_grid_layout.addWidget(QLabel('Game Code'), 1, 0)
        info_grid_layout.addWidget(self.rom_game_code, 1, 1)
        info_grid_layout.addWidget(QLabel('Maker Code'), 2, 0)
        info_grid_layout.addWidget(self.rom_maker_code, 2, 1)
        info_grid_layout.addWidget(QLabel('Secure Area CRC'), 3, 0)
        info_grid_layout.addWidget(self.rom_secure_area_crc, 3, 1)
        info_grid_layout.addWidget(QLabel('Header CRC'), 4, 0)
        info_grid_layout.addWidget(self.rom_header_crc, 4, 1)
        info_grid_layout.addWidget(QLabel('Size'), 5, 0)
        info_grid_layout.addWidget(self.rom_size, 5, 1)

        content_grid_layout.addWidget(QLabel('ARM 9'), 0, 0)
        content_grid_layout.addWidget(self.rom_arm9_size, 0, 1)
        content_grid_layout.addWidget(QLabel('ARM 7'), 1, 0)
        content_grid_layout.addWidget(self.rom_arm7_size, 1, 1)
        content_grid_layout.addWidget(QLabel('Overlay 9'), 2, 0)
        content_grid_layout.addWidget(self.rom_overlay9_size, 2, 1)
        content_grid_layout.addWidget(QLabel('Overlay 7'), 3, 0)
        content_grid_layout.addWidget(self.rom_overlay7_size, 3, 1)
        content_grid_layout.addWidget(QLabel('Data'), 4, 0)
        content_grid_layout.addWidget(self.rom_data_size, 4, 1)
        content_grid_layout.addWidget(QLabel('Overlay'), 5, 0)
        content_grid_layout.addWidget(self.rom_overlay_size, 5, 1)
        content_grid_layout.addWidget(QLabel('Banner'), 6, 0)
        content_grid_layout.addWidget(self.rom_banner_size, 6, 1)
        content_grid_layout.addWidget(QLabel('Header'), 7, 0)
        content_grid_layout.addWidget(self.rom_header_size, 7, 1)

        info_group_box.setLayout(info_grid_layout)
        content_group_box.setLayout(content_grid_layout)

        hbox_layout.addWidget(info_group_box)
        hbox_layout.addWidget(content_group_box)
        self.nds_group_box.setLayout(hbox_layout)

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

        self.tool_bar_encrypt_action = QAction('Encrypt', self)
        self.tool_bar_encrypt_action.triggered.connect(self.encrypt)
        self.tool_bar_encrypt_action.setEnabled(False)

        self.tool_bar_trim_action = QAction('Trim', self)
        self.tool_bar_trim_action.triggered.connect(self.trim)
        self.tool_bar_trim_action.setEnabled(False)

        self.tool_bar_extract_action = QAction('Extract', self)
        self.tool_bar_extract_action.triggered.connect(self.extract)
        self.tool_bar_extract_action.setEnabled(False)

        self.tool_bar_rebuild_action = QAction('Rebuild', self)
        self.tool_bar_rebuild_action.triggered.connect(self.rebuild)
        self.tool_bar_rebuild_action.setEnabled(False)

        self.tool_bar.addAction(self.tool_bar_fix_header_crc_action)
        self.tool_bar.addAction(self.tool_bar_decrypt_action)
        self.tool_bar.addAction(self.tool_bar_encrypt_action)
        self.tool_bar.addAction(self.tool_bar_trim_action)
        self.tool_bar.addAction(self.tool_bar_extract_action)
        self.tool_bar.addAction(self.tool_bar_rebuild_action)

    def enable_functions_callback(self, future):
        """Callback for opening a ROM."""
        if not future.exception():
            self.rom_title.setText(self.rom.title)
            self.rom_game_code.setText(self.rom.game_code)
            self.rom_maker_code.setText(self.rom.maker_code)
            self.rom_size.setText(humanize.naturalsize(self.rom.path.stat().st_size, gnu=True))
            self.rom_secure_area_crc.setText(', '.join(('VALID' if self.rom.is_secure_area_crc_ok else 'INVALID',
                                                        'DECRYPTED' if self.rom.is_decrypted else 'ENCRYPTED')))
            self.rom_header_crc.setText('VALID' if self.rom.is_header_crc_ok else 'INVALID')

            self.tool_bar_fix_header_crc_action.setEnabled(not self.rom.is_header_crc_ok)
            self.tool_bar_extract_action.setEnabled(True)

    def enable_rebuild_callback(self, future):
        """Enables the rebuild QAction."""
        if not future.exception():
            self.rom_arm9_size.setText(humanize.naturalsize(self.rom.arm9_bin.stat().st_size, gnu=True))
            self.rom_arm7_size.setText(humanize.naturalsize(self.rom.arm7_bin.stat().st_size, gnu=True))
            self.rom_overlay9_size.setText(humanize.naturalsize(self.rom.overlay9_bin.stat().st_size, gnu=True))
            self.rom_overlay7_size.setText(humanize.naturalsize(self.rom.overlay7_bin.stat().st_size, gnu=True))
            self.rom_data_size.setText(humanize.naturalsize(self.rom.data_size, gnu=True))
            self.rom_overlay_size.setText(humanize.naturalsize(self.rom.overlay_size, gnu=True))
            self.rom_header_size.setText(humanize.naturalsize(self.rom.header_bin.stat().st_size, gnu=True))
            self.rom_banner_size.setText(humanize.naturalsize(self.rom.banner_bin.stat().st_size, gnu=True))

            self.tool_bar_rebuild_action.setEnabled(True)

    def info_callback(self, future):
        """Refresh ROM information."""
        if not future.exception():
            coro = self.ndstools.info(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_functions_callback)

    def open_file(self):
        """Open a QFileDialog to allow the user to open a file into the application."""
        filename, accepted = QFileDialog().getOpenFileName(self, 'Open File', str(Path.home()), self.filters)

        if accepted:
            path = Path(filename)
            self.tool_bar_rebuild_action.setEnabled(False)
            if path.suffix == '.nds':
                self.rom = NdsRom(path)
            if self.rom:
                coro = self.ndstools.info(self.rom)
                future = asyncio.ensure_future(coro)
                future.add_done_callback(self.enable_functions_callback)

    def fix_header_crc(self):
        """Fix the open ROM's header's CRC."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.fix_header_crc(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.info_callback)

    def decrypt(self):
        """Decrypt the open ROM."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.decrypt(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.info_callback)

    def encrypt(self):
        """Encrypt the open ROM."""
        if isinstance(self.rom, NdsRom):
            if self.rom.maker_code == '01':
                coro = self.ndstools.encrypt_nintendo(self.rom)
            else:
                coro = self.ndstools.encrypt_others(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.info_callback)

    def trim(self):
        """Trim the open ROM."""
        if isinstance(self.rom, NdsRom):
            extract_coro = self.ndstools.extract(self.rom)
            rebuild_coro = self.ndstools.extract(self.rom)
            future = asyncio.gather(extract_coro, rebuild_coro)
            future.add_done_callback(self.info_callback)

    def extract(self):
        """Extract the open ROM."""
        dirname = QFileDialog().getExistingDirectory(self, 'Open File', str(self.rom.extract_dir))

        if dirname:
            self.rom.extract_dir = Path(dirname)
            if isinstance(self.rom, NdsRom):
                coro = self.ndstools.extract(self.rom)
                future = asyncio.ensure_future(coro)
                future.add_done_callback(self.enable_rebuild_callback)

    def rebuild(self):
        """Rebuild the open ROM."""
        if isinstance(self.rom, NdsRom):
            coro = self.ndstools.rebuild(self.rom)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.info_callback)


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

    def excepthook(error, value, traceback):
        print(error, value, traceback)
        sys._excepthook(error, value, traceback)
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


