from pathlib import Path


class NdsRom:
    def __init__(self, path):
        self.path = Path(path)
        self.actual_size = ''
        self.extract_dir = self.path.parent
        self.title = ''
        self.game_code = ''
        self.maker_code = ''
        self.secure_area_crc = ''
        self.decrypted = ''
        self.header_crc = ''

    @property
    def arm9_bin(self):
        return self.extract_dir / self.path.stem / 'arm9.bin'

    @property
    def arm7_bin(self):
        return self.extract_dir / self.path.stem / 'arm7.bin'

    @property
    def overlay9_bin(self):
        return self.extract_dir / self.path.stem / 'overlay9.bin'

    @property
    def overlay7_bin(self):
        return self.extract_dir / self.path.stem / 'overlay7.bin'

    @property
    def data_dir(self):
        return self.extract_dir / self.path.stem / 'data'

    @property
    def overlay_dir(self):
        return self.extract_dir / self.path.stem / 'overlay'

    @property
    def banner_bin(self):
        return self.extract_dir / self.path.stem / 'banner.bin'

    @property
    def header_bin(self):
        return self.extract_dir / self.path.stem / 'header.bin'
