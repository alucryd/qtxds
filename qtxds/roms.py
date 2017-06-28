from pathlib import Path


class NdsRom:
    def __init__(self, path):
        self.path = Path(path)
        self.extract_path = self.path.with_name(self.path.stem)
        self.arm9_bin = self.extract_path / 'arm9.bin'
        self.arm7_bin = self.extract_path / 'arm7.bin'
        self.overlay9_bin = self.extract_path / 'overlay9.bin'
        self.overlay7_bin = self.extract_path / 'overlay7.bin'
        self.data_dir = self.extract_path / 'data'
        self.overlay_dir = self.extract_path / 'overlay'
        self.banner_bmp = self.extract_path / 'banner.bmp'
        self.banner_bin = self.extract_path / 'banner.bin'
        self.header_bin = self.extract_path / 'header.bin'

        self.title = ''
        self.code = ''
        self.maker = ''
        self.decrypted = True
