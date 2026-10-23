#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from shlex import quote


def check_launcher_python():
    interpreter = shutil.which('python3')
    try:
        if interpreter and subprocess.call(
            [interpreter, '-c', 'import sys; sys.exit(sys.version_info < (3, 15))'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) == 0:
            return
    except OSError:
        pass
    sys.exit('Python v3.15+ required for python3 on PATH.')


def cp(src, dest, dryrun=False):
    print('copying file: %s -> %s' % (src, dest))
    if not dryrun:
        shutil.copy(src, dest)


def mkdir(path, dryrun=False):
    print('creating directory:', path)
    if not dryrun and not os.path.exists(path):
        os.makedirs(path)


def parse_arguments():  # noqa
    if sys.version_info < (3, 15):
        sys.exit('Python v3.15+ required.')

    if sys.platform != 'darwin':
        sys.exit('macOS required.')

    default_user_destdir = os.path.join(os.path.expanduser('~'), '.autojump')
    default_user_prefix = ''
    default_system_destdir = '/'
    default_system_prefix = '/usr/local'

    parser = ArgumentParser(
        description='Installs autojump for fish in the current user\'s home \
            directory, or system-wide with --system.',
    )
    parser.add_argument(
        '-n', '--dryrun', action='store_true', default=False,
        help='simulate installation',
    )
    parser.add_argument(
        '-f', '--force', action='store_true', default=False,
        help='skip root user and shell type checks',
    )
    parser.add_argument(
        '-d', '--destdir', metavar='DIR', default=default_user_destdir,
        help='set destination to DIR',
    )
    parser.add_argument(
        '-p', '--prefix', metavar='DIR', default=default_user_prefix,
        help='set prefix to DIR',
    )
    parser.add_argument(
        '-s', '--system', action='store_true', default=False,
        help='install system wide for all users',
    )

    args = parser.parse_args()

    if not args.force:
        if args.system:
            if os.geteuid() != 0:
                print(
                    'Please rerun as root for system-wide installation.',
                    file=sys.stderr,
                )
                sys.exit(1)

        if os.path.basename(os.getenv('SHELL', '')) != 'fish':
            print(
                'Unsupported shell: %s' % os.getenv('SHELL'),
                file=sys.stderr,
            )
            sys.exit(1)

    if args.system:
        if args.destdir != default_user_destdir \
                or args.prefix != default_user_prefix:
            print(
                'Custom paths incompatible with --system option.',
                file=sys.stderr,
            )
            sys.exit(1)

        args.destdir = default_system_destdir
        args.prefix = default_system_prefix

    return args


def show_post_installation_message(share_dir):
    aj_shell = quote(os.path.join(share_dir, 'autojump.fish'))
    source_msg = 'if test -f %s; source %s; end' % (aj_shell, aj_shell)
    print('\nPlease manually add the following line(s) to ~/.config/fish/config.fish:')
    print('\n\t' + source_msg)

    print('\nPlease restart terminal(s) before running autojump.\n')


def main(args):
    check_launcher_python()

    if args.dryrun:
        print('Installing autojump to %s (DRYRUN)...' % args.destdir)
    else:
        print('Installing autojump to %s ...' % args.destdir)

    bin_dir = os.path.join(args.destdir, args.prefix, 'bin')
    doc_dir = os.path.join(args.destdir, args.prefix, 'share', 'man', 'man1')
    share_dir = os.path.join(args.destdir, args.prefix, 'share', 'autojump')

    mkdir(bin_dir, args.dryrun)
    mkdir(doc_dir, args.dryrun)
    mkdir(share_dir, args.dryrun)

    cp('./bin/autojump', bin_dir, args.dryrun)
    cp('./bin/autojump_data.py', bin_dir, args.dryrun)
    cp('./bin/autojump_match.py', bin_dir, args.dryrun)
    cp('./bin/autojump_utils.py', bin_dir, args.dryrun)
    cp('./bin/icon.png', share_dir, args.dryrun)
    cp('./docs/autojump.1', doc_dir, args.dryrun)

    cp('./bin/autojump.fish', share_dir, args.dryrun)
    show_post_installation_message(share_dir)


if __name__ == '__main__':
    sys.exit(main(parse_arguments()))
