#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import errno
import os
import platform
import re
import shutil
import sys
from itertools import islice


def create_dir(path):
    """Creates a directory atomically."""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def first(xs):
    return next(iter(xs), None)


def get_tab_entry_info(entry, separator):
    """
    Given a tab entry in the following format return needle, index, and path:

        [needle]__[index]__[path]
    """
    needle, index, path = None, None, None

    match_needle = re.search(r'(.*?)' + separator, entry)
    match_index = re.search(separator + r'([0-9]{1})', entry)
    match_path = re.search(
        separator + r'[0-9]{1}' + separator + r'(.*)',
        entry,
    )

    if match_needle:
        needle = match_needle.group(1)

    if match_index:
        index = int(match_index.group(1))

    if match_path:
        path = match_path.group(1)

    return needle, index, path


def get_pwd():
    try:
        return os.getcwd()
    except OSError:
        print('Current directory no longer exists.', file=sys.stderr)
        raise


def has_uppercase(string):
    return any(ch.isupper() for ch in string)


def in_bash():
    return 'bash' in os.getenv('SHELL')


def is_autojump_sourced():
    return '1' == os.getenv('AUTOJUMP_SOURCED')


def is_linux():
    return platform.system() == 'Linux'


def is_osx():
    return platform.system() == 'Darwin'


def is_windows():
    return platform.system() == 'Windows'


def last(xs):
    tmp = None
    for tmp in xs:
        pass
    return tmp


def move_file(src, dst):
    """
    Atomically move file.

    Windows does not allow for atomic file renaming (which is used by
    os.rename / shutil.move) so destination paths must first be deleted.
    """
    if is_windows() and os.path.exists(dst):
        # raises exception if file is in use on Windows
        os.remove(dst)
    shutil.move(src, dst)


def print_entry(entry):
    print('%.1f:\t%s' % (entry.weight, entry.path))


def print_tab_menu(needle, tab_entries, separator):
    """
    Prints the tab completion menu according to the following format:

        [needle]__[index]__[possible_match]

    The needle (search pattern) and index are necessary to recreate the results
    on subsequent calls.
    """
    for i, entry in enumerate(tab_entries):
        print(
            '%s%s%d%s%s' % (
                needle,
                separator,
                i + 1,
                separator,
                entry.path,
            ),
        )


def sanitize(directories):
    # edge case to allow '/' as a valid path
    clean = lambda x: x if x == os.sep else x.rstrip(os.sep)
    return list(map(clean, directories))


def second(xs):
    it = iter(xs)
    next(it, None)
    return next(it, None)


def surround_quotes(string):
    """
    Bash has problems dealing with certain paths so we're surrounding all
    path outputs with quotes.
    """
    if in_bash() and string:
        return '"{0}"'.format(string)
    return string


def take(n, iterable):
    """Return first n items of an iterable."""
    return islice(iterable, n)
