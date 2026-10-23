# -*- coding: utf-8 -*-
import os

import autojump_data
import pytest
from autojump_data import dictify
from autojump_data import entriefy
from autojump_data import Entry
from autojump_data import load
from autojump_data import load_backup
from autojump_data import migrate_osx_xdg_data
from autojump_data import save


@pytest.fixture
def config(tmpdir, monkeypatch):
    monkeypatch.setattr(autojump_data, 'is_osx', lambda: False)
    return {
        'data_path': str(tmpdir.join('data', 'autojump.txt')),
        'backup_path': str(tmpdir.join('data', 'autojump.txt.bak')),
    }


def test_entry_iterators_preserve_unicode_paths():
    data = {'/中文 Projects': 10.0, '/日本語': 20.0}
    entries = entriefy(data)
    assert iter(entries) is entries
    assert dictify(entries) == data
    assert list(entries) == []
    assert dictify([Entry('/中文', 5.0)]) == {'/中文': 5.0}


def test_load_missing_database(config):
    assert load(config) == {}


def test_save_utf8_round_trip_and_backup(config):
    data = {'/中文 Projects': 10.0, '/日本語': 2.5}
    save(config, data)
    assert load(config) == data
    with open(config['data_path'], 'rb') as saved:
        content = saved.read()
    assert b'\r\n' not in content
    assert set(content.decode('utf-8').splitlines()) == {
        '10.0\t/中文 Projects', '2.5\t/日本語',
    }
    with open(config['backup_path'], 'rb') as backup:
        assert backup.read() == content

    save(config, {'/中文 Projects': 15.0})
    assert load(config) == {'/中文 Projects': 15.0}
    with open(config['backup_path'], 'rb') as backup:
        assert backup.read() == content


def test_load_existing_utf8_format(config):
    os.makedirs(os.path.dirname(config['data_path']))
    with open(config['data_path'], 'wb') as data:
        data.write('30.0\t/中文 Projects\ninvalid line\n'.encode('utf-8'))
        data.write(b'2.5\t/bad\xffpath\n')
    assert load(config) == {'/中文 Projects': 30.0, '/bad\ufffdpath': 2.5}


def test_restore_backup_replaces_existing_data(config):
    original = {'/中文 Projects': 10.0}
    save(config, original)
    save(config, {'/日本語': 20.0})

    assert load_backup(config) == original
    assert load(config) == original
    assert not os.path.exists(config['backup_path'])


def test_migrate_osx_data_replaces_existing_files(config, tmp_path, monkeypatch):
    save(config, {'/existing': 1.0})
    home = tmp_path / 'home'
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setattr(autojump_data, 'is_osx', lambda: True)
    old_data = home / '.local' / 'share' / 'autojump'
    old_data.mkdir(parents=True)
    (old_data / 'autojump.txt').write_text('10.0\t/中文 Projects\n', encoding='utf-8')
    (old_data / 'autojump.txt.bak').write_text('5.0\t/日本語\n', encoding='utf-8')

    migrate_osx_xdg_data(config)

    assert load(config) == {'/中文 Projects': 10.0}
    with open(config['backup_path'], encoding='utf-8') as backup:
        assert backup.read() == '5.0\t/日本語\n'
    assert not old_data.exists()
