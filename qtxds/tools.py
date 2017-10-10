import asyncio
import re
import shutil
import subprocess
import sys


class Tools:
    def __init__(self, tool, status_bar):
        self.status_bar = status_bar
        self.path = shutil.which(tool)

        if sys.platform == 'win32':
            self.encoding = 'cp1252'
        else:
            self.encoding = 'utf8'


class NdsTools(Tools):
    def __init__(self, status_bar):
        Tools.__init__(self, 'ndstool', status_bar)

    async def info(self, rom):
        self.status_bar.showMessage('Analyzing...')

        # Get information
        cmd = [str(self.path), '-i', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        while True:
            data = await proc.stdout.readline()
            line = data.decode(self.encoding).rstrip()
            if line:
                if line.startswith('0x00'):
                    rom.title = line.split()[-1]
                    continue
                if line.startswith('0x0C'):
                    rom.game_code = line.split()[-1][1:-1]
                    continue
                if line.startswith('0x10'):
                    rom.maker_code = line.split()[-1][1:-1]
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

        # Get actual size
        cmd = [str(self.path), '-l', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        rom.actual_size = 0
        while True:
            data = await proc.stdout.readline()
            line = data.decode(self.encoding).strip()
            if line:
                if line[0].isdigit():
                    rom.actual_size += int(line.split()[3])
            else:
                break

        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def fix_header_crc(self, rom):
        self.status_bar.showMessage('Fixing Header CRC...')

        cmd = [str(self.path), '-f', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def encrypt_nintendo(self, rom):
        self.status_bar.showMessage('Encrypting (Nintendo)...')

        cmd = [str(self.path), '-se', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def encrypt_others(self, rom):
        self.status_bar.showMessage('Encrypting (others)...')

        cmd = [str(self.path), '-sE', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def decrypt(self, rom):
        self.status_bar.showMessage('Decrypting...')

        cmd = [str(self.path), '-sd', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def extract(self, rom):
        self.status_bar.showMessage('Extracting...')

        (rom.extract_dir / rom.path.stem).mkdir(exist_ok=True)

        cmd = [str(self.path), '-x', str(rom.path)]
        cmd += ['-9', str(rom.arm9_bin)]
        cmd += ['-7', str(rom.arm7_bin)]
        cmd += ['-y9', str(rom.overlay9_bin)]
        cmd += ['-y7', str(rom.overlay7_bin)]
        cmd += ['-d', str(rom.data_dir)]
        cmd += ['-y', str(rom.overlay_dir)]
        cmd += ['-t', str(rom.banner_bin)]
        cmd += ['-h', str(rom.header_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def rebuild(self, rom):
        self.status_bar.showMessage('Rebuilding...')

        # Backup original ROM
        src = rom.path
        dst = rom.path.with_suffix('.nds.old')
        if not dst.exists():
            shutil.copyfile(src, dst)

        cmd = [str(self.path), '-c', str(rom.path)]
        cmd += ['-9', str(rom.arm9_bin)]
        cmd += ['-7', str(rom.arm7_bin)]
        cmd += ['-y9', str(rom.overlay9_bin)]
        cmd += ['-y7', str(rom.overlay7_bin)]
        cmd += ['-d', str(rom.data_dir)]
        cmd += ['-y', str(rom.overlay_dir)]
        cmd += ['-t', str(rom.banner_bin)]
        cmd += ['-h', str(rom.header_bin)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')


class ThreedsTools(Tools):
    def __init__(self, status_bar):
        Tools.__init__(self, '3dstools', status_bar)
