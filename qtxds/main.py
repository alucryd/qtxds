import asyncio
import sys
from pathlib import Path

import humanize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog, QHBoxLayout, QLabel, QMainWindow,
                             QVBoxLayout, QDesktopWidget, QGridLayout, QGroupBox, QLineEdit)
from quamash import QEventLoop

from qtxds.roms import NdsRom, ThreedsRom
from tools import NdsTool, ThreedsTool, CtrTool


class MainWindow(QMainWindow):
    """Create the main window that stores all of the widgets necessary for the application."""

    def __init__(self, parent=None):
        """Initialize the components of the main window."""
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('qtxds')

        self.main_grid()
        self.setCentralWidget(self.rom_group_box)

        self.menu_bar = self.menuBar()
        self.about_dialog = AboutDialog()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        self.file_menu()
        self.extract_menu()
        self.rebuild_menu()
        self.convert_menu()
        self.encryption_menu()
        self.padding_menu()
        self.misc_menu()
        self.help_menu()

        self.rom = None
        self.ndstool = NdsTool()
        self.ctrtool = CtrTool()
        self.threedstool = ThreedsTool()

        filters = ['Nintendo DS/3DS ROMs (*.nds *.3ds)', 'Nintendo DS ROMs (*.nds)', 'Nintendo 3DS ROMs (*.3ds)']
        self.filters = ';;'.join(filters)

    def main_grid(self):
        self.rom_group_box = QGroupBox("ROM")

        hbox_layout = QHBoxLayout()

        info_group_box = QGroupBox('General Information')
        nds_content_group_box = QGroupBox('NDS Content')
        threeds_content_group_box = QGroupBox('3DS Content')

        info_grid_layout = QGridLayout()
        nds_content_grid_layout = QGridLayout()
        threeds_content_grid_layout = QGridLayout()

        self.rom_title = QLineEdit()
        self.rom_maker_code = QLineEdit()
        self.rom_product_code = QLineEdit()
        self.rom_secure_area_crc = QLabel()
        self.rom_decrypted = QLabel()
        self.rom_header_crc = QLabel()
        self.rom_size = QLabel()
        self.rom_content_size = QLabel()

        # NDS Content
        self.rom_arm9_size = QLabel()
        self.rom_arm7_size = QLabel()
        self.rom_overlay9_size = QLabel()
        self.rom_overlay7_size = QLabel()
        self.rom_data_size = QLabel()
        self.rom_overlay_size = QLabel()
        self.rom_banner_size = QLabel()
        self.rom_header_size = QLabel()

        # 3DS Content
        self.rom_extended_header_size = QLabel()
        self.rom_plain_size = QLabel()
        self.rom_logo_size = QLabel()
        self.rom_exefs_size = QLabel()
        self.rom_romfs_size = QLabel()

        info_grid_layout.addWidget(QLabel('Title'), 0, 0)
        info_grid_layout.addWidget(self.rom_title, 0, 1)
        info_grid_layout.addWidget(QLabel('Maker Code'), 1, 0)
        info_grid_layout.addWidget(self.rom_maker_code, 1, 1)
        info_grid_layout.addWidget(QLabel('Product Code'), 2, 0)
        info_grid_layout.addWidget(self.rom_product_code, 2, 1)
        info_grid_layout.addWidget(QLabel('Secure Area CRC'), 3, 0)
        info_grid_layout.addWidget(self.rom_secure_area_crc, 3, 1)
        info_grid_layout.addWidget(QLabel('Header CRC'), 4, 0)
        info_grid_layout.addWidget(self.rom_header_crc, 4, 1)
        info_grid_layout.addWidget(QLabel('Size'), 5, 0)
        info_grid_layout.addWidget(self.rom_size, 5, 1)
        info_grid_layout.addWidget(QLabel('Content Size'), 6, 0)
        info_grid_layout.addWidget(self.rom_content_size, 6, 1)

        nds_content_grid_layout.addWidget(QLabel('ARM 9'), 0, 0)
        nds_content_grid_layout.addWidget(self.rom_arm9_size, 0, 1)
        nds_content_grid_layout.addWidget(QLabel('ARM 7'), 1, 0)
        nds_content_grid_layout.addWidget(self.rom_arm7_size, 1, 1)
        nds_content_grid_layout.addWidget(QLabel('Overlay 9'), 2, 0)
        nds_content_grid_layout.addWidget(self.rom_overlay9_size, 2, 1)
        nds_content_grid_layout.addWidget(QLabel('Overlay 7'), 3, 0)
        nds_content_grid_layout.addWidget(self.rom_overlay7_size, 3, 1)
        nds_content_grid_layout.addWidget(QLabel('Data'), 4, 0)
        nds_content_grid_layout.addWidget(self.rom_data_size, 4, 1)
        nds_content_grid_layout.addWidget(QLabel('Overlay'), 5, 0)
        nds_content_grid_layout.addWidget(self.rom_overlay_size, 5, 1)
        nds_content_grid_layout.addWidget(QLabel('Banner'), 6, 0)
        nds_content_grid_layout.addWidget(self.rom_banner_size, 6, 1)
        nds_content_grid_layout.addWidget(QLabel('Header'), 7, 0)
        nds_content_grid_layout.addWidget(self.rom_header_size, 7, 1)

        threeds_content_grid_layout.addWidget(QLabel('Extended Header'), 0, 0)
        threeds_content_grid_layout.addWidget(self.rom_extended_header_size, 0, 1)
        threeds_content_grid_layout.addWidget(QLabel('Plain Region'), 1, 0)
        threeds_content_grid_layout.addWidget(self.rom_plain_size, 1, 1)
        threeds_content_grid_layout.addWidget(QLabel('Logo Region'), 2, 0)
        threeds_content_grid_layout.addWidget(self.rom_logo_size, 2, 1)
        threeds_content_grid_layout.addWidget(QLabel('ExeFS'), 3, 0)
        threeds_content_grid_layout.addWidget(self.rom_exefs_size, 3, 1)
        threeds_content_grid_layout.addWidget(QLabel('RomFS'), 4, 0)
        threeds_content_grid_layout.addWidget(self.rom_romfs_size, 4, 1)

        info_group_box.setLayout(info_grid_layout)
        nds_content_group_box.setLayout(nds_content_grid_layout)
        threeds_content_group_box.setLayout(threeds_content_grid_layout)

        hbox_layout.addWidget(info_group_box)
        hbox_layout.addWidget(nds_content_group_box)
        hbox_layout.addWidget(threeds_content_group_box)
        self.rom_group_box.setLayout(hbox_layout)

    def file_menu(self):
        """Create a file submenu with an Open ROM item that opens a file dialog."""
        self.file_sub_menu = self.menu_bar.addMenu('File')

        self.open_action = QAction('Open ROM', self)
        self.open_action.setStatusTip('Open a ROM into qtxds.')
        self.open_action.setShortcut('CTRL+O')
        self.open_action.triggered.connect(self.open_file)

        self.exit_action = QAction('Exit Application', self)
        self.exit_action.setStatusTip('Exit the application.')
        self.exit_action.setShortcut('CTRL+Q')
        self.exit_action.triggered.connect(lambda: QApplication.quit())

        self.file_sub_menu.addAction(self.open_action)
        self.file_sub_menu.addAction(self.exit_action)

    def extract_menu(self):
        """Create an extract submenu with various extract actions."""
        self.extract_sub_menu = self.menu_bar.addMenu('Extract')

        self.extract_all_action = QAction('Extract all', self)
        self.extract_all_action.setStatusTip('Extract the open ROM.')
        self.extract_all_action.setShortcut('CTRL+E')
        self.extract_all_action.triggered.connect(self.extract_all)
        self.extract_all_action.setEnabled(False)

        self.extract_cci_action = QAction('Extract CCI', self)
        self.extract_cci_action.setStatusTip('Extract the NCSD contents of the open ROM.')
        self.extract_cci_action.triggered.connect(self.extract_cci)
        self.extract_cci_action.setEnabled(False)

        self.extract_cxi_action = QAction('Extract CXI', self)
        self.extract_cxi_action.setStatusTip('Extract the NCCH contents of the open ROM.')
        self.extract_cxi_action.triggered.connect(self.extract_cxi)
        self.extract_cxi_action.setEnabled(False)

        self.extract_exefs_action = QAction('Extract ExeFS', self)
        self.extract_exefs_action.setStatusTip('Extract the ExeFS contents of the open ROM.')
        self.extract_exefs_action.triggered.connect(self.extract_exefs)
        self.extract_exefs_action.setEnabled(False)

        self.extract_romfs_action = QAction('Extract RomFS', self)
        self.extract_romfs_action.setStatusTip('Extract the RomFS contents of the open ROM.')
        self.extract_romfs_action.triggered.connect(self.extract_romfs)
        self.extract_romfs_action.setEnabled(False)

        self.extract_sub_menu.addAction(self.extract_all_action)
        self.extract_sub_menu.addAction(self.extract_cci_action)
        self.extract_sub_menu.addAction(self.extract_cxi_action)
        self.extract_sub_menu.addAction(self.extract_exefs_action)
        self.extract_sub_menu.addAction(self.extract_romfs_action)

    def rebuild_menu(self):
        """Create a rebuild submenu with various rebuild actions."""
        self.rebuild_sub_menu = self.menu_bar.addMenu('Rebuild')

        self.rebuild_all_action = QAction('Rebuild all', self)
        self.rebuild_all_action.setStatusTip('Rebuild all contents of the open ROM.')
        self.rebuild_all_action.setShortcut('CTRL+R')
        self.rebuild_all_action.triggered.connect(self.rebuild_all)
        self.rebuild_all_action.setEnabled(False)

        self.rebuild_cci_action = QAction('Rebuild CCI', self)
        self.rebuild_cci_action.setStatusTip('Rebuild the NCSD contents of the open ROM.')
        self.rebuild_cci_action.triggered.connect(self.rebuild_cci)
        self.rebuild_cci_action.setEnabled(False)

        self.rebuild_cxi_action = QAction('Rebuild CXI', self)
        self.rebuild_cxi_action.setStatusTip('Rebuild the NCCH contents of the open ROM.')
        self.rebuild_cxi_action.triggered.connect(self.rebuild_cxi)
        self.rebuild_cxi_action.setEnabled(False)

        self.rebuild_exefs_action = QAction('Rebuild ExeFS', self)
        self.rebuild_exefs_action.setStatusTip('Rebuild the ExeFS contents of the open ROM.')
        self.rebuild_exefs_action.triggered.connect(self.rebuild_exefs)
        self.rebuild_exefs_action.setEnabled(False)

        self.rebuild_romfs_action = QAction('Rebuild RomFS', self)
        self.rebuild_romfs_action.setStatusTip('Rebuild the RomFS contents of the open ROM.')
        self.rebuild_romfs_action.triggered.connect(self.rebuild_romfs)
        self.rebuild_romfs_action.setEnabled(False)

        self.rebuild_sub_menu.addAction(self.rebuild_all_action)
        self.rebuild_sub_menu.addAction(self.rebuild_cci_action)
        self.rebuild_sub_menu.addAction(self.rebuild_cxi_action)
        self.rebuild_sub_menu.addAction(self.rebuild_exefs_action)
        self.rebuild_sub_menu.addAction(self.rebuild_romfs_action)

    def convert_menu(self):
        """Create a convert submenu with various convert actions."""
        self.convert_sub_menu = self.menu_bar.addMenu('Convert')

        self.convert_cia_action = QAction('Convert to CIA', self)
        self.convert_cia_action.setStatusTip('Convert the open ROM to the CIA format.')
        self.convert_cia_action.triggered.connect(self.convert_cia)
        self.convert_cia_action.setEnabled(False)

        self.convert_sub_menu.addAction(self.convert_cia_action)

    def encryption_menu(self):
        """Create an encryption submenu with decrypt and encrypt actions."""
        self.encryption_sub_menu = self.menu_bar.addMenu('Encryption')

        self.decrypt_action = QAction('Decrypt', self)
        self.decrypt_action.setStatusTip('Decrypt the open ROM.')
        self.decrypt_action.triggered.connect(self.decrypt)
        self.decrypt_action.setEnabled(False)

        self.encrypt_action = QAction('Encrypt', self)
        self.encrypt_action.setStatusTip('Encrypt the open ROM.')
        self.encrypt_action.triggered.connect(self.encrypt)
        self.encrypt_action.setEnabled(False)

        self.encryption_sub_menu.addAction(self.decrypt_action)
        self.encryption_sub_menu.addAction(self.encrypt_action)

    def padding_menu(self):
        """Create a padding submenu with trim and pad actions."""
        self.padding_sub_menu = self.menu_bar.addMenu('Padding')

        self.trim_action = QAction('Trim', self)
        self.trim_action.setStatusTip('Trim the open ROM.')
        self.trim_action.setShortcut('CTRL+T')
        self.trim_action.triggered.connect(self.trim)
        self.trim_action.setEnabled(False)

        self.pad_action = QAction('Pad', self)
        self.pad_action.setStatusTip('Pad the open ROM.')
        self.pad_action.setShortcut('CTRL+P')
        self.pad_action.triggered.connect(self.pad)
        self.pad_action.setEnabled(False)

        self.padding_sub_menu.addAction(self.trim_action)
        self.padding_sub_menu.addAction(self.pad_action)

    def misc_menu(self):
        """Create a misc submenu with various actions."""
        self.misc_sub_menu = self.menu_bar.addMenu('Misc')

        self.fix_header_crc_action = QAction('Fix Header CRC', self)
        self.fix_header_crc_action.setStatusTip('Fix the open ROM\'s header CRC.')
        self.fix_header_crc_action.triggered.connect(self.fix_header_crc)
        self.fix_header_crc_action.setEnabled(False)

        self.misc_sub_menu.addAction(self.fix_header_crc_action)

    def help_menu(self):
        """Create a help submenu with an About item tha opens an about dialog."""
        self.help_sub_menu = self.menu_bar.addMenu('Help')

        self.about_action = QAction('About', self)
        self.about_action.setStatusTip('About the application.')
        self.about_action.setShortcut('CTRL+H')
        self.about_action.triggered.connect(lambda: self.about_dialog.exec_())

        self.help_sub_menu.addAction(self.about_action)

    def open_file_callback(self, future):
        """Callback for opening a ROM."""
        if not future.exception():
            self.rom_title.setText(self.rom.title)
            self.rom_product_code.setText(self.rom.product_code)
            self.rom_maker_code.setText(self.rom.maker_code)
            self.rom_size.setText(humanize.naturalsize(self.rom.size, gnu=True))
            self.rom_content_size.setText(humanize.naturalsize(self.rom.content_size, gnu=True))
            self.extract_all_action.setEnabled(True)
            self.extract_cci_action.setEnabled(isinstance(self.rom, ThreedsRom))
            self.convert_cia_action.setEnabled(isinstance(self.rom, ThreedsRom))
            self.trim_action.setEnabled(True)
            self.pad_action.setEnabled(isinstance(self.rom, ThreedsRom))
            if isinstance(self.rom, NdsRom):
                self.rom_secure_area_crc.setText(', '.join(('VALID' if self.rom.is_secure_area_crc_ok else 'INVALID',
                                                            'DECRYPTED' if self.rom.is_decrypted else 'ENCRYPTED')))
                self.rom_header_crc.setText('VALID' if self.rom.is_header_crc_ok else 'INVALID')
                self.rom_extended_header_size.setText('')
                self.rom_plain_size.setText('')
                self.rom_logo_size.setText('')
                self.rom_exefs_size.setText('')
                self.rom_romfs_size.setText('')
                self.fix_header_crc_action.setEnabled(not self.rom.is_header_crc_ok)
            elif isinstance(self.rom, ThreedsRom):
                self.rom_secure_area_crc.setText('')
                self.rom_header_crc.setText('')
                self.rom_arm9_size.setText('')
                self.rom_arm7_size.setText('')
                self.rom_overlay9_size.setText('')
                self.rom_overlay7_size.setText('')
                self.rom_data_size.setText('')
                self.rom_overlay_size.setText('')
                self.rom_banner_size.setText('')
                self.rom_header_size.setText('')
                self.rom_extended_header_size.setText(humanize.naturalsize(self.rom.extended_header_size, gnu=True))
                self.rom_plain_size.setText(humanize.naturalsize(self.rom.plain_size, gnu=True))
                self.rom_logo_size.setText(humanize.naturalsize(self.rom.logo_size, gnu=True))
                self.rom_exefs_size.setText(humanize.naturalsize(self.rom.exefs_size, gnu=True))
                self.rom_romfs_size.setText(humanize.naturalsize(self.rom.romfs_size, gnu=True))
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def enable_rebuild_all_callback(self, future):
        """Enables the rebuild QAction."""
        if not future.exception():
            self.rebuild_all_action.setEnabled(True)
            if isinstance(self.rom, NdsRom):
                self.rom_arm9_size.setText(humanize.naturalsize(self.rom.arm9_bin.stat().st_size, gnu=True))
                self.rom_arm7_size.setText(humanize.naturalsize(self.rom.arm7_bin.stat().st_size, gnu=True))
                self.rom_overlay9_size.setText(humanize.naturalsize(self.rom.overlay9_bin.stat().st_size, gnu=True))
                self.rom_overlay7_size.setText(humanize.naturalsize(self.rom.overlay7_bin.stat().st_size, gnu=True))
                self.rom_data_size.setText(humanize.naturalsize(self.rom.data_size, gnu=True))
                self.rom_overlay_size.setText(humanize.naturalsize(self.rom.overlay_size, gnu=True))
                self.rom_header_size.setText(humanize.naturalsize(self.rom.header_bin.stat().st_size, gnu=True))
                self.rom_banner_size.setText(humanize.naturalsize(self.rom.banner_bin.stat().st_size, gnu=True))
            elif isinstance(self.rom, ThreedsRom):
                self.extract_cxi_action.setEnabled(True)
                self.extract_exefs_action.setEnabled(True)
                self.extract_romfs_action.setEnabled(True)
                self.rebuild_cci_action.setEnabled(True)
                self.rebuild_cxi_action.setEnabled(True)
                self.rebuild_exefs_action.setEnabled(True)
                self.rebuild_romfs_action.setEnabled(True)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def info_callback(self, future):
        """Refresh ROM information."""
        if not future.exception():
            coro = self.rom.info(self.status_bar)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.open_file_callback)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def extract_cci_callback(self, future):
        """Callback for the Extract CCI action."""
        if not future.exception():
            self.rebuild_cci_action.setEnabled(True)
            self.extract_cxi_action.setEnabled(True)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def extract_cxi_callback(self, future):
        """Callback for the Extract CXI action."""
        if not future.exception():
            self.rebuild_cxi_action.setEnabled(True)
            self.extract_exefs_action.setEnabled(True)
            self.extract_romfs_action.setEnabled(True)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def extract_exefs_callback(self, future):
        """Callback for the Extract ExeFS action."""
        if not future.exception():
            self.rebuild_exefs_action.setEnabled(True)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def extract_romfs_callback(self, future):
        """Callback for the Extract RomFS action."""
        if not future.exception():
            self.rebuild_romfs_action.setEnabled(True)
        else:
            self.status_bar.showMessage('Error')

        self.status_bar.showMessage('Ready')

    def open_file(self):
        """Open a QFileDialog to allow the user to open a file into the application."""
        filename, accepted = QFileDialog().getOpenFileName(self, 'Open File', str(Path.home()), self.filters)

        if accepted:
            path = Path(filename)
            for action in (
                    'extract_cci',
                    'extract_cxi',
                    'extract_exefs',
                    'extract_romfs',
                    'rebuild_all',
                    'rebuild_cci',
                    'rebuild_cxi',
                    'rebuild_exefs',
                    'rebuild_romfs',
                    'decrypt',
                    'encrypt',
                    'trim',
                    'pad',
                    'fix_header_crc'
            ):
                getattr(self, f'{action}_action').setEnabled(False)
            if path.suffix == '.nds':
                self.rom = NdsRom(path)
            elif path.suffix == '.3ds':
                self.rom = ThreedsRom(path)
            if self.rom:
                coro = self.rom.info(self.status_bar)
                future = asyncio.ensure_future(coro)
                future.add_done_callback(self.open_file_callback)

    def decrypt(self):
        """Decrypt the open ROM."""
        coro = self.rom.decrypt(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def encrypt(self):
        """Encrypt the open ROM."""
        coro = self.rom.encrypt(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def trim(self):
        """Trim the open ROM."""
        coro = self.rom.trim(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def pad(self):
        """Pad the open ROM."""
        coro = self.rom.pad(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def extract_all(self):
        """Extract the open ROM."""
        dirname = QFileDialog().getExistingDirectory(self, 'Open Directory', str(self.rom.working_dir))

        if dirname:
            self.rom.working_dir = Path(dirname)
            coro = self.rom.extract_all(self.status_bar)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.enable_rebuild_all_callback)

    def extract_cci(self):
        """Extract the NCSD contents of the open ROM."""
        coro = self.rom.extract_cci(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.extract_cci_callback)

    def extract_cxi(self):
        """Extract the NCCH contents of the open ROM."""
        coro = self.rom.extract_cxi(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.extract_cxi_callback)

    def extract_exefs(self):
        """Extract the ExeFS contents of the open ROM."""
        coro = self.rom.extract_exefs(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.extract_exefs_callback)

    def extract_romfs(self):
        """Extract the RomFS contents of the open ROM."""
        coro = self.rom.extract_romfs(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.extract_romfs_callback)

    def rebuild_all(self):
        """Rebuild the open ROM."""
        coro = self.rom.rebuild(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def rebuild_cci(self):
        """Rebuild the NCSD contents of the open ROM."""
        coro = self.rom.rebuild_cci(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def rebuild_cxi(self):
        """Rebuild the NCCH contents of the open ROM."""
        coro = self.rom.rebuild_cxi(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def rebuild_exefs(self):
        """Rebuild the ExeFS contents of the open ROM."""
        coro = self.rom.rebuild_exefs(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def rebuild_romfs(self):
        """Rebuild the RomFS contents of the open ROM."""
        coro = self.rom.rebuild_romfs(self.status_bar)
        future = asyncio.ensure_future(coro)
        future.add_done_callback(self.info_callback)

    def convert_cia(self):
        """Convert the open ROM to the CIA format."""
        dirname = QFileDialog().getExistingDirectory(self, 'Open Directory', str(self.rom.working_dir))

        if dirname:
            print(dirname)
            self.rom.working_dir = Path(dirname)
            coro = self.rom.convert_cia(self.status_bar)
            future = asyncio.ensure_future(coro)
            future.add_done_callback(self.info_callback)

    def fix_header_crc(self):
        """Fix the open ROM's header CRC."""
        coro = self.ndstool.fix_header_crc(self.rom)
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
    asyncio.set_event_loop(loop)

    window = MainWindow()
    desktop = QDesktopWidget().availableGeometry()
    width = (desktop.width() - window.width()) / 2
    height = (desktop.height() - window.height()) / 2
    window.show()
    window.move(width, height)

    with loop:
        loop.run_forever()
