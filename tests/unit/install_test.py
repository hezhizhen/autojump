# -*- coding: utf-8 -*-
import os
import runpy
import sys
from types import SimpleNamespace

import pytest

import install
import uninstall

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def installer(monkeypatch):
    monkeypatch.setenv('SHELL', '/bin/zsh')
    monkeypatch.setattr(sys, 'argv', ['install.py', '--dryrun'])
    return install


@pytest.mark.parametrize('version', [(2, 7), (3, 3), (3, 14)])
@pytest.mark.parametrize('script', ['bin/autojump', 'install.py', 'uninstall.py'])
def test_reject_unsupported_python(monkeypatch, version, script):
    parse_arguments = runpy.run_path(os.path.join(ROOT, script))['parse_arguments']
    monkeypatch.setitem(
        parse_arguments.__globals__, 'sys', SimpleNamespace(
            version_info=version, exit=sys.exit,
        ),
    )
    with pytest.raises(SystemExit, match=r'Python v3\.15\+ required\.'):
        parse_arguments()


def test_accept_python315(installer, monkeypatch):
    monkeypatch.setattr(installer, 'sys', SimpleNamespace(version_info=(3, 15)))
    assert installer.parse_arguments().dryrun


@pytest.mark.parametrize('script', ['install.py', 'uninstall.py'])
def test_default_dry_run(cli, script):
    result = cli('--dryrun', script=script)
    assert result.returncode == 0
    assert 'DRYRUN' in result.stdout


def test_custom_install_and_legacy_uninstall(installer, tmpdir, monkeypatch, cli):
    destination = str(tmpdir.join('installation'))
    clink_dir = str(tmpdir.mkdir('clink'))
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(
        sys, 'argv', [
            'install.py', '--destdir', destination, '--clinkdir', clink_dir,
        ],
    )
    args = installer.parse_arguments()
    installer.main(args)
    bin_dir = os.path.join(destination, 'bin')
    assert not os.path.exists(os.path.join(bin_dir, 'autojump_argparse.py'))
    result = cli('--version', script=os.path.join(bin_dir, 'autojump'))
    assert result.returncode == 0
    assert result.stdout.startswith('autojump v')
    assert not result.stderr
    with open(os.path.join(bin_dir, 'autojump_argparse.py'), 'w') as legacy:
        legacy.write('# old installation\n')

    uninstall.remove_custom_installation(args)
    assert not os.path.exists(destination)
