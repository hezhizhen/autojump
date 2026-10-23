#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from autojump_utils import first
from autojump_utils import get_tab_entry_info
from autojump_utils import has_uppercase
from autojump_utils import last
from autojump_utils import sanitize
from autojump_utils import second
from autojump_utils import take


def test_has_uppercase():
    assert has_uppercase('Foo')
    assert has_uppercase('foO')
    assert not has_uppercase('foo')
    assert not has_uppercase('')
    assert has_uppercase('日本語Ａ')
    assert not has_uppercase('中文路径')


def test_sanitize():
    assert sanitize([]) == []
    assert sanitize([r'/foo/bar/', r'/']) == ['/foo/bar', '/']
    assert sanitize(['/中文 Projects/']) == ['/中文 Projects']


# iteration
def test_first():
    assert first(range(5)) == 0
    assert first(iter([1])) == 1
    assert first([]) is None


def test_second():
    assert second(range(5)) == 1
    assert second(iter([1, 2])) == 2
    assert second([1]) is None
    assert second([]) is None


def test_last():
    assert last(range(4)) == 3
    assert last(iter([1])) == 1
    assert last([]) is None


def test_take():
    assert list(take(1, range(3))) == [0]
    assert list(take(2, range(3))) == [0, 1]
    assert list(take(4, range(3))) == [0, 1, 2]
    assert list(take(10, [])) == []


# helper functions
def test_get_needle():
    assert get_tab_entry_info('foo__', '__') == ('foo', None, None)


def test_get_index():
    assert get_tab_entry_info('foo__2', '__') == ('foo', 2, None)


def test_get_path():
    assert get_tab_entry_info('foo__3__/foo/bar', '__') \
        == ('foo', 3, '/foo/bar')


def test_get_none():
    assert get_tab_entry_info('gibberish content', '__') == (None, None, None)
