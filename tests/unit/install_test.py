# -*- coding: utf-8 -*-
import os
import runpy
import sys
from shlex import quote
from types import SimpleNamespace

import pytest

import install
import uninstall

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def installer(monkeypatch):
    monkeypatch.setenv('SHELL', '/bin/zsh')
    monkeypatch.setenv(
        'PATH', os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH', ''),
    )
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
    monkeypatch.setattr(installer, 'sys', SimpleNamespace(version_info=(3, 15), platform='darwin'))
    assert installer.parse_arguments().dryrun


@pytest.mark.parametrize('platform', ['linux', 'freebsd', 'win32'])
@pytest.mark.parametrize('script', ['bin/autojump', 'install.py', 'uninstall.py'])
def test_reject_unsupported_platform(monkeypatch, platform, script):
    parse_arguments = runpy.run_path(os.path.join(ROOT, script))['parse_arguments']
    monkeypatch.setitem(
        parse_arguments.__globals__, 'sys', SimpleNamespace(
            version_info=(3, 15), platform=platform, exit=sys.exit,
        ),
    )
    with pytest.raises(SystemExit, match=r'macOS required\.'):
        parse_arguments()


@pytest.mark.parametrize('script', ['install.py', 'uninstall.py'])
def test_default_dry_run(cli, script):
    result = cli('--dryrun', script=script)
    assert result.returncode == 0
    assert 'DRYRUN' in result.stdout


@pytest.mark.parametrize('force', [False, True])
@pytest.mark.parametrize('version', [None, (3, 14)])
def test_install_rejects_bad_launcher(cli, tmpdir, version, force):
    path = tmpdir.mkdir('interpreter path')
    if version is not None:
        launcher = path.join('python3')
        probe = 'import sys; sys.version_info = %r; exec(sys.argv[2])' % (version,)
        launcher.write('#!/bin/sh\nexec %s -c %s "$@"\n' % (quote(sys.executable), quote(probe)))
        launcher.chmod(0o755)
    destination = str(tmpdir.join('installation'))
    args = ['--destdir', destination]
    if force:
        args.append('--force')
    result = cli(*args, script='install.py', cwd=ROOT, env={'PATH': str(path)})
    assert result.returncode == 1
    assert 'Python v3.15+ required for python3 on PATH.' in result.stderr
    assert not os.path.exists(destination)


@pytest.mark.parametrize('direct', [False, True])
def test_custom_install_and_legacy_uninstall(installer, tmpdir, monkeypatch, cli, direct):
    destination = str(tmpdir.join('installation'))
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(
        sys, 'argv', ['install.py', '--destdir', destination],
    )
    args = installer.parse_arguments()
    installer.main(args)
    bin_dir = os.path.join(destination, 'bin')
    assert not os.path.exists(os.path.join(bin_dir, 'autojump_argparse.py'))
    result = cli('--version', script=os.path.join(bin_dir, 'autojump'), direct=direct)
    assert result.returncode == 0
    assert result.stdout.startswith('autojump v')
    assert not result.stderr
    with open(os.path.join(bin_dir, 'autojump_argparse.py'), 'w') as legacy:
        legacy.write('# old installation\n')

    uninstall.remove_custom_installation(args)
    assert not os.path.exists(destination)


def test_remove_user_data_uses_macos_directory(tmp_path, monkeypatch):
    home = tmp_path / 'home'
    data = home / 'Library' / 'autojump'
    data.mkdir(parents=True)
    xdg_data = tmp_path / 'xdg-data'
    xdg_data.mkdir()
    (xdg_data / 'unrelated.txt').write_text('keep me')
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setenv('XDG_DATA_HOME', str(xdg_data))

    uninstall.remove_user_data()

    assert not data.exists()
    assert (xdg_data / 'unrelated.txt').read_text() == 'keep me'
