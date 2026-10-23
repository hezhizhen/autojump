# -*- coding: utf-8 -*-
import os
import sys
from types import SimpleNamespace

import pytest

import uninstall


@pytest.fixture
def legacy_installation(tmp_path):
    def create(prefix, zshshare):
        share_dir = tmp_path / prefix / 'share' / 'autojump'
        profile_dir = tmp_path / 'etc' / 'profile.d'
        completion_dir = tmp_path / zshshare
        legacy_files = [
            profile_dir / 'autojump.sh',
            completion_dir / '_j',
        ] + [share_dir / ('autojump.' + shell) for shell in ['bash', 'fish', 'tcsh', 'zsh']]
        unrelated_files = [profile_dir / 'other.sh', completion_dir / '_other']
        for path in legacy_files + unrelated_files:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('keep original contents\n')
        return legacy_files, unrelated_files

    return create


@pytest.mark.parametrize('dryrun', [False, True])
@pytest.mark.parametrize('zshshare', ['functions', 'legacy completions/site-functions'])
def test_custom_uninstall_cleans_legacy_files(tmp_path, monkeypatch, legacy_installation, dryrun, zshshare):
    legacy_files, unrelated_files = legacy_installation('local', zshshare)
    argv = ['uninstall.py', '--destdir', str(tmp_path), '--prefix', 'local']
    if zshshare != 'functions':
        argv.extend(['--zshshare', zshshare])
    if dryrun:
        argv.append('--dryrun')
    monkeypatch.setattr(sys, 'argv', argv)
    args = uninstall.parse_arguments()

    uninstall.remove_custom_installation(args, args.dryrun)

    for path in legacy_files:
        assert path.exists() is dryrun
    for path in unrelated_files:
        assert path.read_text() == 'keep original contents\n'


@pytest.mark.parametrize('dryrun', [False, True])
def test_system_uninstall_cleans_legacy_files(tmp_path, monkeypatch, legacy_installation, dryrun):
    legacy_files, unrelated_files = legacy_installation('usr/local', 'usr/local/share/zsh/site-functions')

    def join(first, *parts):
        if first == '/':
            return str(tmp_path.joinpath(*(part.lstrip('/') for part in parts)))
        return os.path.join(first, *parts)

    monkeypatch.setattr(
        uninstall, 'os', SimpleNamespace(
            path=SimpleNamespace(join=join, exists=os.path.exists),
            geteuid=lambda: 0,
            remove=os.remove,
        ),
    )

    uninstall.remove_system_installation(dryrun)

    for path in legacy_files:
        assert path.exists() is dryrun
    for path in unrelated_files:
        assert path.read_text() == 'keep original contents\n'
