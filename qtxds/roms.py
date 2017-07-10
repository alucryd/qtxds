import os
from pathlib import Path


class NdsRom:
    def __init__(self, path):
        self.path = Path(path)
        self.title = ''
        self.game_code = ''
        self.maker_code = ''
        self.capacity = 0
        self.is_header_crc_ok = True
        self.is_secure_area_crc_ok = True
        self.is_decrypted = True

        self.extract_dir = self.path.parent
        self.arm9_bin = self.extract_dir / self.path.stem / 'arm9.bin'
        self.arm7_bin = self.extract_dir / self.path.stem / 'arm7.bin'
        self.overlay9_bin = self.extract_dir / self.path.stem / 'overlay9.bin'
        self.overlay7_bin = self.extract_dir / self.path.stem / 'overlay7.bin'
        self.banner_bin = self.extract_dir / self.path.stem / 'banner.bin'
        self.data_dir = self.extract_dir / self.path.stem / 'data'
        self.overlay_dir = self.extract_dir / self.path.stem / 'overlay'
        self.header_bin = self.extract_dir / self.path.stem / 'header.bin'

    @staticmethod
    def _directory_size(path):
        size = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                size += Path(root, filename).stat().st_size
        return size

    @property
    def data_size(self):
        return self._directory_size(self.data_dir)

    @property
    def overlay_size(self):
        return self._directory_size(self.overlay_dir)
