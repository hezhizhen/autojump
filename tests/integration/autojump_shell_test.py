# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.parametrize('shell', ['bash', 'zsh', 'fish'])
def test_macos_shell_navigation_and_finder(cli, tmp_path, shell):
    executable = shutil.which(shell)
    if executable is None:
        pytest.skip('%s is not installed' % shell)

    target = tmp_path / '中文 Projects'
    target.mkdir()
    assert cli('--add', str(target)).returncode == 0
    launchers = tmp_path / 'launchers'
    launchers.mkdir()
    opener = launchers / 'open'
    opener.write_text('#!/bin/sh\nprintf \'%s\\n\' "$@" >> "$AUTOJUMP_TEST_OPEN_LOG"\n')
    opener.chmod(0o755)
    open_log = tmp_path / 'opened.txt'
    env = cli.env.copy()
    env.update({
        'PATH': os.pathsep.join([
            str(launchers), os.path.dirname(sys.executable), os.path.join(ROOT, 'bin'), env.get('PATH', ''),
        ]),
        'XDG_DATA_HOME': str(tmp_path / 'xdg-data'),
        'AUTOJUMP_TEST_SOURCE': os.path.join(ROOT, 'bin', 'autojump.' + shell),
        'AUTOJUMP_TEST_OPEN_LOG': str(open_log),
    })
    options = {'bash': ['--noprofile', '--norc'], 'zsh': ['-f'], 'fish': ['--no-config']}
    script = '\n'.join([
        'source "$AUTOJUMP_TEST_SOURCE"',
        'printf \'%s\\n\' "$AUTOJUMP_ERROR_PATH"',
        'jo 中文',
        'jco 中文',
        'jc 中文 >/dev/null',
        'pwd',
    ])
    if shell == 'zsh':
        # Sandboxed runs cannot adjust background process priority.
        script = 'unsetopt bgnice\n' + script

    result = subprocess.run(
        [executable] + options[shell] + ['-c', script],
        cwd=tmp_path, env=env, capture_output=True, text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == os.path.join(env['HOME'], 'Library', 'autojump', 'errors.log')
    assert lines[-1] == str(target)
    assert open_log.read_text().splitlines() == [str(target), str(target)]
    assert not (tmp_path / 'xdg-data' / 'autojump').exists()
