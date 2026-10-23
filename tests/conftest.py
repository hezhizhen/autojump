# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from collections import namedtuple

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'bin'))

CommandResult = namedtuple('CommandResult', ['returncode', 'stdout', 'stderr'])


@pytest.fixture
def cli(tmpdir):
    home = str(tmpdir.mkdir('home'))
    env = os.environ.copy()
    env.update({
        'HOME': home,
        'USERPROFILE': home,
        'APPDATA': home,
        'LOCALAPPDATA': home,
        'XDG_DATA_HOME': os.path.join(home, '.local', 'share'),
        'AUTOJUMP_SOURCED': '1',
        'SHELL': '/bin/zsh',
        'PYTHON_COLORS': '0',
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONDONTWRITEBYTECODE': '1',
    })

    def run(*args, **kwargs):
        script = kwargs.pop('script', os.path.join('bin', 'autojump'))
        command = [os.path.join(ROOT, script)] + list(args)
        if not kwargs.pop('direct', False):
            command.insert(0, sys.executable)
        process_env = env.copy()
        process_env.update(kwargs.pop('env', {}))
        process = subprocess.Popen(
            command,
            cwd=kwargs.pop('cwd', str(tmpdir)),
            env=process_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        return CommandResult(
            process.returncode,
            stdout.decode('utf-8'),
            stderr.decode('utf-8'),
        )

    if sys.platform == 'darwin':
        data_home = os.path.join(home, 'Library')
    elif sys.platform == 'win32':
        data_home = home
    else:
        data_home = env['XDG_DATA_HOME']
    run.data_path = os.path.join(data_home, 'autojump', 'autojump.txt')
    return run
