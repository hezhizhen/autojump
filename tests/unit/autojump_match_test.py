#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from autojump_data import Entry
from autojump_match import match_anywhere
from autojump_match import match_consecutive


@pytest.mark.parametrize('matcher', [match_anywhere, match_consecutive])
@pytest.mark.parametrize(
    'path, needles, ignore_case', [
        ('/opt/Program Files (x86)/GIMP', ['program files (x86)', 'gimp'], True),
        (r'/data/back\slash/(archive)', [r'back\slash', '(archive)'], False),
    ],
)
def test_special_characters_in_paths(matcher, path, needles, ignore_case):
    entry = Entry(path, 10)
    assert list(matcher(needles, [entry], ignore_case)) == [entry]


class TestMatchAnywhere(object):

    entry1 = Entry('/foo/bar/baz', 10)
    entry2 = Entry('/baz/foo/bar', 10)
    entry3 = Entry('/foo/baz', 10)
    entry4 = Entry('/中/zhong/国/guo', 10)
    entry5 = Entry('/is\'t/this/a/b*tchin/edge/case?', 10)

    @pytest.fixture
    def haystack(self):
        return [
            self.entry1,
            self.entry2,
            self.entry3,
            self.entry4,
            self.entry5,
        ]

    def test_single_needle(self, haystack):
        assert list(match_anywhere(['bar'], haystack)) == [self.entry1, self.entry2]

    def test_consecutive(self, haystack):
        assert list(match_anywhere(['foo', 'bar'], haystack)) \
            == [self.entry1, self.entry2]
        assert list(match_anywhere(['bar', 'foo'], haystack)) == []

    def test_skip(self, haystack):
        assert list(match_anywhere(['baz', 'bar'], haystack)) == [self.entry2]
        assert list(match_anywhere(['中', '国'], haystack)) == [self.entry4]

    def test_ignore_case(self, haystack):
        assert list(match_anywhere(['bAz', 'bAR'], haystack, ignore_case=True)) \
            == [self.entry2]

    def test_wildcard_in_needle(self, haystack):
        # https://github.com/wting/autojump/issues/402
        assert list(match_anywhere(['*', 'this'], haystack)) == []
        assert list(match_anywhere(['this', '*'], haystack)) == [self.entry5]


class TestMatchConsecutive(object):

    entry1 = Entry('/foo/bar/baz', 10)
    entry2 = Entry('/baz/foo/bar', 10)
    entry3 = Entry('/foo/baz', 10)
    entry4 = Entry('/中/zhong/国/guo', 10)
    entry5 = Entry('/日/本', 10)
    entry6 = Entry('/is\'t/this/a/b*tchin/edge/case?', 10)

    @pytest.fixture
    def haystack(self):
        return [
            self.entry1,
            self.entry2,
            self.entry3,
            self.entry4,
            self.entry5,
        ]

    def test_single_needle(self, haystack):
        assert list(match_consecutive(['baz'], haystack)) == [self.entry1, self.entry3]
        assert list(match_consecutive(['本'], haystack)) == [self.entry5]

    def test_consecutive(self, haystack):
        assert list(match_consecutive(['bar', 'baz'], haystack)) == [self.entry1]
        assert list(match_consecutive(['foo', 'bar'], haystack)) == [self.entry2]
        assert list(match_consecutive(['国', 'guo'], haystack)) == [self.entry4]
        assert list(match_consecutive(['bar', 'foo'], haystack)) == []

    def test_ignore_case(self, haystack):
        assert list(match_consecutive(['FoO', 'bAR'], haystack, ignore_case=True)) \
            == [self.entry2]

    @pytest.mark.xfail(reason='https://github.com/wting/autojump/issues/402')
    def test_wildcard_in_needle(self, haystack):
        assert list(match_consecutive(['*', 'this'], haystack)) == []
        assert list(match_consecutive(['*', 'edge', 'case'], haystack)) == [self.entry6]
