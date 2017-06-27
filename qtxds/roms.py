import subprocess
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
        self.banner_bin = self.extract_path / 'banner.bin'
        self.header_bin = self.extract_path / 'header.bin'

    def extract(self):
        self.extract_path.mkdir(exist_ok=True)
        cmd = ['ndstool', '-x', self.path, '-9', self.arm9_bin, '-7', self.arm7_bin, '-y9', self.overlay9_bin,
               '-y7', self.overlay7_bin, '-d', self.data_dir, '-y', self.overlay_dir, '-t', self.banner_bin,
               '-h', self.header_bin]
        subprocess.run(cmd)
