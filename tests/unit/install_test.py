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
    monkeypatch.setenv('SHELL', 'fish')
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


@pytest.mark.parametrize('shell', ['/usr/local/bin/fish', '/opt/homebrew/bin/fish', 'fish'])
def test_accept_fish(installer, monkeypatch, shell):
    monkeypatch.setenv('SHELL', shell)
    assert installer.parse_arguments().dryrun


@pytest.mark.parametrize('shell', ['other-shell', ''])
def test_reject_unsupported_shell(installer, monkeypatch, capsys, shell):
    monkeypatch.setenv('SHELL', shell)
    with pytest.raises(SystemExit) as error:
        installer.parse_arguments()
    assert error.value.code == 1
    assert 'Unsupported shell:' in capsys.readouterr().err


def test_force_install_for_fish_with_other_login_shell(installer, monkeypatch, capsys):
    monkeypatch.setenv('SHELL', 'other-shell')
    monkeypatch.setattr(sys, 'argv', ['install.py', '--dryrun', '--force'])
    installer.main(installer.parse_arguments())
    assert '~/.config/fish/config.fish' in capsys.readouterr().out


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
        launcher.write('#!%s\nimport sys\nsys.version_info = %r\nexec(sys.argv[2])\n' % (sys.executable, version))
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
@pytest.mark.parametrize('prefix', ['', 'local'])
def test_custom_install_and_legacy_uninstall(installer, tmpdir, monkeypatch, cli, direct, prefix):
    destination = str(tmpdir.join('installation path'))
    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(
        sys, 'argv', ['install.py', '--destdir', destination, '--prefix', prefix],
    )
    args = installer.parse_arguments()
    installer.main(args)
    bin_dir = os.path.join(destination, prefix, 'bin')
    share_dir = os.path.join(destination, prefix, 'share', 'autojump')
    assert sorted(os.listdir(destination)) == (['bin', 'share'] if not prefix else [prefix])
    assert sorted(os.listdir(share_dir)) == ['autojump.fish', 'icon.png']
    assert not os.path.exists(os.path.join(bin_dir, 'autojump_argparse.py'))
    result = cli('--version', script=os.path.join(bin_dir, 'autojump'), direct=direct)
    assert result.returncode == 0
    assert result.stdout.startswith('autojump v')
    assert not result.stderr
    with open(os.path.join(bin_dir, 'autojump_argparse.py'), 'w') as legacy:
        legacy.write('# old installation\n')

    monkeypatch.setattr(
        sys, 'argv', ['uninstall.py', '--destdir', destination, '--prefix', prefix],
    )
    uninstall.remove_custom_installation(uninstall.parse_arguments())
    assert not os.path.exists(destination)


def test_custom_dry_run_does_not_create_files(cli, tmp_path):
    destination = tmp_path / 'installation'
    result = cli('--dryrun', '--destdir', str(destination), script='install.py', cwd=ROOT)
    assert result.returncode == 0
    assert 'autojump.fish' in result.stdout
    assert not destination.exists()


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
