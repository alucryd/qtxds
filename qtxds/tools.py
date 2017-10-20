import asyncio
import re
import shutil
import sys


class Tool:
    def __init__(self, tool):
        self.path = shutil.which(tool)

        if sys.platform == 'win32':
            self.encoding = 'cp1252'
        else:
            self.encoding = 'utf8'


class NdsTool(Tool):
    def __init__(self):
        super().__init__('ndstool')

    async def info(self, rom, status_bar):
        status_bar.showMessage('Analyzing...')

        cmd = [str(self.path), '-i', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        while True:
            data = await proc.stdout.readline()
            line = data.decode(self.encoding).strip()
            if line:
                if line.startswith('0x00'):
                    rom.title = line.split()[-1]
                    continue
                if line.startswith('0x10'):
                    rom.maker_code = line.split()[3]
                    continue
                if line.startswith('0x0C'):
                    rom.product_code = line.split()[-1][1:-1]
                    continue
                if line.startswith('0x6C'):
                    secure_area_crc, decrypted = re.findall('\(.*\)', line)[-1][1:-1].split(', ')
                    rom.is_secure_area_crc_ok = secure_area_crc == 'OK'
                    rom.is_decrypted = decrypted == 'decrypted'
                    continue
                if line.startswith('0x15E'):
                    header_crc = line.split()[-1][1:-1]
                    rom.is_header_crc_ok = header_crc == 'OK'
                    continue
            else:
                break

        await proc.wait()

        cmd = [str(self.path), '-l', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        rom.content_size = 0
        while True:
            data = await proc.stdout.readline()
            line = data.decode(self.encoding).strip()
            if line:
                if line[0].isdigit():
                    rom.content_size += int(line.split()[3])
            else:
                break

        await proc.wait()

    async def fix_header_crc(self, rom, status_bar):
        status_bar.showMessage('Fixing Header CRC...')

        cmd = [str(self.path), '-f', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def encrypt_nintendo(self, rom, status_bar):
        status_bar.showMessage('Encrypting (Nintendo)...')

        cmd = [str(self.path), '-se', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def encrypt_others(self, rom, status_bar):
        status_bar.showMessage('Encrypting (others)...')

        cmd = [str(self.path), '-sE', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def decrypt(self, rom, status_bar):
        status_bar.showMessage('Decrypting...')

        cmd = [str(self.path), '-sd', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def extract_all(self, rom, status_bar):
        status_bar.showMessage('Extracting...')

        rom.extract_dir.mkdir(exist_ok=True)

        cmd = [str(self.path), '-x', str(rom.path)]
        cmd += ['-9', str(rom.arm9_bin)]
        cmd += ['-7', str(rom.arm7_bin)]
        cmd += ['-y9', str(rom.overlay9_bin)]
        cmd += ['-y7', str(rom.overlay7_bin)]
        cmd += ['-d', str(rom.data_dir)]
        cmd += ['-y', str(rom.overlay_dir)]
        cmd += ['-t', str(rom.banner_bin)]
        cmd += ['-h', str(rom.header_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def rebuild_all(self, rom, status_bar):
        rom.backup(status_bar)

        status_bar.showMessage('Rebuilding...')

        cmd = [str(self.path), '-c', str(rom.path)]
        cmd += ['-9', str(rom.arm9_bin)]
        cmd += ['-7', str(rom.arm7_bin)]
        cmd += ['-y9', str(rom.overlay9_bin)]
        cmd += ['-y7', str(rom.overlay7_bin)]
        cmd += ['-d', str(rom.data_dir)]
        cmd += ['-y', str(rom.overlay_dir)]
        cmd += ['-t', str(rom.banner_bin)]
        cmd += ['-h', str(rom.header_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()


class ThreedsTool(Tool):
    def __init__(self):
        Tool.__init__(self, '3dstool')

    async def extract_cci(self, rom, status_bar):
        status_bar.showMessage('Extracting CCI...')

        rom.extract_dir.mkdir(exist_ok=True)

        cmd = [str(self.path), '-x']
        cmd += ['-f', str(rom.path)]
        cmd += ['-t', 'cci']
        cmd += ['--header', str(rom.ncsd_header_bin)]
        cmd += ['-0', str(rom.game_cxi)]
        cmd += ['-1', str(rom.manual_cfa)]
        cmd += ['-2', str(rom.download_play_cfa)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def extract_cxi(self, rom, status_bar):
        status_bar.showMessage('Extracting CXI...')

        cmd = [str(self.path), '-x']
        cmd += ['-f', str(rom.game_cxi)]
        cmd += ['-t', 'cxi']
        cmd += ['--header', str(rom.ncch_header_bin)]
        cmd += ['--exh', str(rom.extended_header_bin)]
        cmd += ['--plain', str(rom.plain_bin)]
        cmd += ['--logo', str(rom.logo_bin)]
        cmd += ['--exefs', str(rom.exefs_bin)]
        cmd += ['--romfs', str(rom.romfs_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def extract_exefs(self, rom, status_bar):
        status_bar.showMessage('Extracting ExeFS...')

        cmd = [str(self.path), '-x']
        cmd += ['-f', str(rom.exefs_bin)]
        cmd += ['-t', 'exefs']
        cmd += ['--header', str(rom.exefs_header_bin)]
        cmd += ['--exefs-dir', str(rom.exefs_dir)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def extract_romfs(self, rom, status_bar):
        status_bar.showMessage('Extracting RomFS...')

        cmd = [str(self.path), '-x']
        cmd += ['-f', str(rom.romfs_bin)]
        cmd += ['-t', 'romfs']
        cmd += ['--romfs-dir', str(rom.romfs_dir)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def extract_all(self, rom, status_bar):
        await self.extract_cci(rom, status_bar)
        await self.extract_cxi(rom, status_bar)
        await self.extract_exefs(rom, status_bar)
        await self.extract_romfs(rom, status_bar)

    async def rebuild_cci(self, rom, status_bar):
        rom.backup(status_bar)

        status_bar.showMessage('Rebuilding CCI...')

        cmd = [str(self.path), '-c']
        cmd += ['-f', str(rom.path)]
        cmd += ['-t', 'cci']
        cmd += ['--header', str(rom.ncsd_header_bin)]
        cmd += ['-0', str(rom.game_cxi)]
        cmd += ['-1', str(rom.manual_cfa)]
        cmd += ['-2', str(rom.download_play_cfa)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def rebuild_cxi(self, rom, status_bar):
        status_bar.showMessage('Rebuilding CXI...')

        cmd = [str(self.path), '-c']
        cmd += ['-f', str(rom.game_cxi)]
        cmd += ['-t', 'cxi']
        cmd += ['--header', str(rom.ncch_header_bin)]
        cmd += ['--exh', str(rom.extended_header_bin)]
        cmd += ['--plain', str(rom.plain_bin)]
        cmd += ['--logo', str(rom.logo_bin)]
        cmd += ['--exefs', str(rom.exefs_bin)]
        cmd += ['--romfs', str(rom.romfs_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def rebuild_exefs(self, rom, status_bar):
        status_bar.showMessage('Rebuilding ExeFS...')

        cmd = [str(self.path), '-c']
        cmd += ['-f', str(rom.exefs_bin)]
        cmd += ['-t', 'exefs']
        cmd += ['--header', str(rom.exefs_header_bin)]
        cmd += ['--exefs-dir', str(rom.exefs_dir)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def rebuild_romfs(self, rom, status_bar):
        status_bar.showMessage('Rebuilding RomFS...')

        cmd = [str(self.path), '-c']
        cmd += ['-f', str(rom.romfs_bin)]
        cmd += ['-t', 'romfs']
        cmd += ['--romfs-dir', str(rom.romfs_dir)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def rebuild_all(self, rom, status_bar):
        await self.rebuild_romfs(rom, status_bar)
        await self.rebuild_exefs(rom, status_bar)
        await self.rebuild_cxi(rom, status_bar)
        await self.rebuild_cci(rom, status_bar)

    async def trim(self, rom, status_bar):
        rom.backup(status_bar)

        status_bar.showMessage('Trimming...')

        cmd = [str(self.path), '-r']
        cmd += ['-f', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

    async def pad(self, rom, status_bar):
        rom.backup(status_bar)

        status_bar.showMessage('Padding...')

        cmd = [str(self.path), '-p']
        cmd += ['-f', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()


class CtrTool(Tool):
    def __init__(self):
        Tool.__init__(self, 'ctrtool')

    async def info(self, rom, status_bar):
        status_bar.showMessage('Analyzing...')

        cmd = [str(self.path), '-i', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        while not proc.stdout.at_eof():
            data = await proc.stdout.readline()
            line = data.decode(self.encoding).strip()
            if line:
                if line.startswith('Media size:'):
                    rom.media_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('> Mediaunit size:'):
                    rom.media_unit_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('Maker code:'):
                    rom.maker_code = line.split(':')[-1].strip()
                    continue
                if line.startswith('Product code:'):
                    rom.product_code = line.split(':')[-1].strip()
                    continue
                if line.startswith('Content size:'):
                    rom.content_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('Exheader size:'):
                    rom.extended_header_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('Plain region size:'):
                    rom.plain_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('Logo size:'):
                    rom.logo_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('ExeFS size:'):
                    rom.exefs_size = int(line.split(':')[-1].strip(), 16)
                    continue
                if line.startswith('RomFS size:'):
                    rom.romfs_size = int(line.split(':')[-1].strip(), 16)
                    continue

        await proc.wait()


class ThreedsConv(Tool):
    def __init__(self):
        super().__init__('3dsconv')

    async def convert(self, rom, status_bar):
        status_bar.showMessage('Converting to CIA...')

        cmd = [str(self.path), '--overwrite', '--output=' + str(rom.working_dir), str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()



