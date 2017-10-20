import os
import shutil
from pathlib import Path

from tools import NdsTool, CtrTool, ThreedsTool, ThreedsConv


class Rom:
    def __init__(self, path):
        self.path = Path(path)
        self.working_dir = self.path.parent
        self.title = ''
        self.maker_code = ''
        self.product_code = ''
        self.content_size = 0

    @property
    def extract_dir(self):
        return self.working_dir / self.path.stem

    def backup(self, status_bar):
        status_bar.showMessage('Backing up...')

        src = self.path
        dst = self.path.with_suffix(self.path.suffix + '.old')
        if not dst.exists():
            shutil.copyfile(src, dst)

    def clean(self, status_bar):
        status_bar.showMessage('Cleaning...')

        shutil.rmtree(self.extract_dir)


class NdsRom(Rom):
    ndstool = NdsTool()

    def __init__(self, path):
        super().__init__(path)

        self.is_header_crc_ok = True
        self.is_secure_area_crc_ok = True
        self.is_decrypted = True

        self.arm9_bin = self.extract_dir / 'arm9.bin'
        self.arm7_bin = self.extract_dir / 'arm7.bin'
        self.overlay9_bin = self.extract_dir / 'overlay9.bin'
        self.overlay7_bin = self.extract_dir / 'overlay7.bin'
        self.banner_bin = self.extract_dir / 'banner.bin'
        self.data_dir = self.extract_dir / 'data'
        self.overlay_dir = self.extract_dir / 'overlay'
        self.header_bin = self.extract_dir / 'header.bin'

    @staticmethod
    def _directory_size(path):
        size = 0
        for root, dirnames, filenames in os.walk(path):
            for filename in filenames:
                size += Path(root, filename).stat().st_size
        return size

    @property
    def size(self):
        return self.path.stat().st_size

    @property
    def data_size(self):
        return self._directory_size(self.data_dir)

    @property
    def overlay_size(self):
        return self._directory_size(self.overlay_dir)

    async def info(self, status_bar):
        await NdsRom.ndstool.info(self, status_bar)

    async def extract_all(self, status_bar):
        await NdsRom.ndstool.extract_all(self, status_bar)

    async def rebuild_all(self, status_bar):
        await NdsRom.ndstool.rebuild_all(self, status_bar)

    async def trim(self, status_bar):
        await NdsRom.ndstool.extract_all(self, status_bar)
        await NdsRom.ndstool.rebuild_all(self, status_bar)

    async def decrypt(self, status_bar):
        await NdsRom.ndstool.decrypt(self, status_bar)

    async def encrypt(self, status_bar):
        if self.maker_code == '01':
            await NdsRom.ndstool.encrypt_nintendo(self, status_bar)
        else:
            await NdsRom.ndstool.encrypt_others(self, status_bar)

    async def fix_header_crc(self, status_bar):
        await NdsRom.ndstool.fix_header_crc(self, status_bar)


class ThreedsRom(Rom):
    ctrtool = CtrTool()
    threedstool = ThreedsTool()
    threedsconv = ThreedsConv()

    def __init__(self, path):
        super().__init__(path)

        self.media_size = 0
        self.media_unit_size = 0
        self.extended_header_size = 0
        self.plain_size = 0
        self.logo_size = 0
        self.exefs_size = 0
        self.romfs_size = 0

        self.ncsd_header_bin = self.extract_dir / 'ncsd_header.bin'
        self.game_cxi = self.extract_dir / 'game.cxi'
        self.manual_cfa = self.extract_dir / 'manual.cfa'
        self.download_play_cfa = self.extract_dir / 'download_play.cfa'
        self.ncch_header_bin = self.extract_dir / 'ncch_header.bin'
        self.extended_header_bin = self.extract_dir / 'extended_header.bin'
        self.plain_bin = self.extract_dir / 'plain.bin'
        self.logo_bin = self.extract_dir / 'logo.bin'
        self.exefs_bin = self.extract_dir / 'exefs.bin'
        self.exefs_header_bin = self.extract_dir / 'exefs_header.bin'
        self.romfs_bin = self.extract_dir / 'romfs.bin'
        self.exefs_dir = self.extract_dir / 'exefs'
        self.romfs_dir = self.extract_dir / 'romfs'

    @property
    def size(self):
        return self.media_size * self.media_unit_size

    async def info(self, status_bar):
        await ThreedsRom.ctrtool.info(self, status_bar)

    async def extract_all(self, status_bar):
        await ThreedsRom.threedstool.extract_all(self, status_bar)

    async def extract_cci(self, status_bar):
        await ThreedsRom.threedstool.extract_cci(self, status_bar)

    async def extract_cxi(self, status_bar):
        await ThreedsRom.threedstool.extract_cxi(self, status_bar)

    async def extract_exefs(self, status_bar):
        await ThreedsRom.threedstool.extract_exefs(self, status_bar)

    async def extract_romfs(self, status_bar):
        await ThreedsRom.threedstool.extract_romfs(self, status_bar)

    async def rebuild_all(self, status_bar):
        await ThreedsRom.threedstool.rebuild_all(self, status_bar)

    async def rebuild_cci(self, status_bar):
        await ThreedsRom.threedstool.rebuild_cci(self, status_bar)

    async def rebuild_cxi(self, status_bar):
        await ThreedsRom.threedstool.rebuild_cxi(self, status_bar)

    async def rebuild_exefs(self, status_bar):
        await ThreedsRom.threedstool.rebuild_exefs(self, status_bar)

    async def rebuild_romfs(self, status_bar):
        await ThreedsRom.threedstool.rebuild_romfs(self, status_bar)

    async def convert_cia(self, status_bar):
        await ThreedsRom.threedsconv.convert(self, status_bar)

    async def trim(self, status_bar):
        await ThreedsRom.threedstool.trim(self, status_bar)

    async def pad(self, status_bar):
        await ThreedsRom.threedstool.pad(self, status_bar)
