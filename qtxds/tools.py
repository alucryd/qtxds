import asyncio
import shutil
import subprocess

import sys

from PyQt5.QtWidgets import QApplication


class NdsTools:
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self.path = shutil.which('ndstool')

    async def info(self, rom):
        cmd = [str(self.path), '-i', str(rom.path)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        proc = await create

        while True:
            data = await proc.stdout.readline()
            line = data.decode('utf8').rstrip()
            if line:
                if line.startswith('0x00'):
                    rom.title = line.split()[-1]
                    continue
                if line.startswith('0x0C'):
                    rom.code = line.split()[-1][1:-1]
                    continue
                if line.startswith('0x10'):
                    rom.maker = line.split()[-1][1:-1]
                    continue
            else:
                break

    async def extract(self, rom):
        self.status_bar.showMessage('Extracting...')

        rom.extract_path.mkdir(exist_ok=True)

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

    async def extract_banner_bmp(self, rom):
        self.status_bar.showMessage('Extracting...')

        rom.extract_path.mkdir(exist_ok=True)

        cmd = [str(self.path), '-x', str(rom.path)]
        cmd += ['-b', str(rom.banner_bmp)]

        create = asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL)
        proc = await create
        await proc.wait()

        self.status_bar.showMessage('Ready')

    async def rebuild(self, rom):
        self.status_bar.showMessage('Extracting...')

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

