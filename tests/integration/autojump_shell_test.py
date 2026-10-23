# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.parametrize('install_prefix', [None, '', 'local'])
def test_macos_fish_navigation_and_finder(cli, tmp_path, install_prefix):
    executable = shutil.which('fish')
    if executable is None:
        pytest.skip('fish is not installed')

    target = tmp_path / '中文 Projects'
    target.mkdir()
    assert cli('--add', str(target)).returncode == 0
    bin_dir = os.path.join(ROOT, 'bin')
    startup = 'source "$AUTOJUMP_TEST_SOURCE"'
    if install_prefix is not None:
        destination = tmp_path / "autojump install's path"
        installation = cli(
            '--destdir', str(destination), '--prefix', install_prefix,
            script='install.py', cwd=ROOT,
        )
        assert installation.returncode == 0, installation.stderr
        bin_dir = os.path.join(str(destination), install_prefix, 'bin')
        startup = next(line.strip() for line in installation.stdout.splitlines() if line.startswith('\tif test -f '))
    launchers = tmp_path / 'launchers'
    launchers.mkdir()
    opener = launchers / 'open'
    opener.write_text(
        '#!%s\nimport os\nimport sys\n'
        'with open(os.environ["AUTOJUMP_TEST_OPEN_LOG"], "a") as log:\n'
        '    log.write("\\n".join(sys.argv[1:]) + "\\n")\n' % sys.executable,
    )
    opener.chmod(0o755)
    open_log = tmp_path / 'opened.txt'
    env = cli.env.copy()
    env.update({
        'PATH': os.pathsep.join([
            str(launchers), os.path.dirname(sys.executable), bin_dir, env.get('PATH', ''),
        ]),
        'XDG_DATA_HOME': str(tmp_path / 'xdg-data'),
        'SHELL': executable,
        'AUTOJUMP_TEST_SOURCE': os.path.join(ROOT, 'bin', 'autojump.fish'),
        'AUTOJUMP_TEST_OPEN_LOG': str(open_log),
    })
    script = '\n'.join([
        startup,
        'printf \'%s\\n\' "$AUTOJUMP_ERROR_PATH"',
        'autojump --complete 中文',
        'jo 中文',
        'jco 中文',
        'jc 中文 >/dev/null',
        'pwd',
    ])
    result = subprocess.run(
        [executable, '--no-config', '-c', script],
        cwd=tmp_path, env=env, capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == os.path.join(env['HOME'], 'Library', 'autojump', 'errors.log')
    assert lines[1] == '中文__1__' + str(target)
    assert lines[-1] == str(target)
    assert open_log.read_text().splitlines() == [str(target), str(target)]
    assert not (tmp_path / 'xdg-data' / 'autojump').exists()
