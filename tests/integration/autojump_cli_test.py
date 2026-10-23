# -*- coding: utf-8 -*-
import os

import pytest


@pytest.mark.parametrize('script', ['bin/autojump', 'install.py', 'uninstall.py'])
def test_help_outside_source_directory(cli, script):
    result = cli('--help', script=script)
    assert result.returncode == 0
    assert result.stdout.startswith('usage: ')
    assert not result.stderr


@pytest.mark.parametrize('option', ['-v', '--version'])
def test_version_uses_stdout(cli, option):
    result = cli(option)
    assert result.returncode == 0
    assert result.stdout.startswith('autojump v')
    assert not result.stderr


@pytest.mark.parametrize('args', [('--unknown',), ('-i', 'invalid'), ('--add',)])
def test_invalid_arguments(cli, args):
    result = cli(*args)
    assert result.returncode == 2
    assert not result.stdout
    assert 'error:' in result.stderr


def test_empty_database(cli):
    assert cli().stdout.strip() == '.'
    assert cli('missing').stdout.strip() == '.'


def test_existing_utf8_database_and_completion(cli, tmpdir):
    directory = str(tmpdir.mkdir('中文 Projects'))
    os.makedirs(os.path.dirname(cli.data_path))
    with open(cli.data_path, 'w', encoding='utf-8') as data:
        data.write('30.0\t%s\n' % directory)

    result = cli('中文')
    assert result.returncode == 0
    assert result.stdout.strip() == directory
    assert not result.stderr
    assert cli('中文', 'Projects').stdout.strip() == directory

    completion = cli('--complete', '中文')
    assert completion.returncode == 0
    assert completion.stdout.splitlines()[0] == '中文__1__' + directory
    assert cli('中文__1__').stdout.strip() == directory
    assert cli('中文__1__' + directory).stdout.strip() == directory


def test_add_update_and_purge(cli, tmpdir):
    directory = str(tmpdir.mkdir('日本語 project'))
    assert cli('--add', directory).returncode == 0
    assert cli('日本語').stdout.strip() == directory
    increased = cli('--increase', '5', cwd=directory)
    assert increased.returncode == 0
    assert increased.stdout.strip() == '11.2:\t' + directory
    decreased = cli('--decrease', '3', cwd=directory)
    assert decreased.returncode == 0
    assert decreased.stdout.strip() == '8.2:\t' + directory
    stats = cli('--stat')
    assert stats.returncode == 0
    assert '1:\t number of entries' in stats.stdout
    assert '8.2:\t' + directory in stats.stdout
    assert os.path.isfile(cli.data_path + '.bak')

    assert cli('--add', str(tmpdir.join('missing'))).returncode == 0
    purged = cli('--purge')
    assert purged.returncode == 0
    assert purged.stdout.strip() == 'Purged 1 entries.'
    assert cli('日本語').stdout.strip() == directory


def test_smartcase_and_weighted_order(cli, tmpdir):
    upper = str(tmpdir.mkdir('FooProject'))
    lower = str(tmpdir.mkdir('fooproject-other'))
    assert cli('--add', upper).returncode == 0
    assert cli('--add', lower).returncode == 0
    assert cli('--add', lower).returncode == 0
    assert cli('foo').stdout.strip() == lower
    assert cli('Foo').stdout.strip() == upper
