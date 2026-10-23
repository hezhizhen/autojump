NAME
----

autojump - a faster way to navigate your filesystem

DESCRIPTION
-----------

autojump is a faster way to navigate your filesystem. It works by
maintaining a database of the directories you use the most from the
command line.

*Directories must be visited first before they can be jumped to.*

USAGE
-----

`j` is a convenience wrapper function around `autojump`. Any option that
can be used with `autojump` can be used with `j` and vice versa.

-   Jump To A Directory That Contains `foo`:

        j foo

-   Jump To A Directory That Contains `foo`, Preferring Child Directories:

    You can prioritize child directories over matches in the databases via

        jc foo

-   Open File Manager To Directories (instead of jumping):

    Instead of jumping to a directory, you can open the directory in Finder.

        jo music

    Opening a file manager to a child directory is also supported:

        jco images

-   Using Multiple Arguments:

    Let's assume the following database:

        30   /Users/user/mail/inbox
        10   /Users/user/work/inbox

    `j in` would jump into /Users/user/mail/inbox as the higher
    weighted entry. However you can pass multiple arguments to autojump
    to prefer a different entry. In the above example, `j w in` would
    then change directory to /Users/user/work/inbox.

For more options refer to help:

    autojump --help

INSTALLATION
------------

### REQUIREMENTS

-   Python v3.15+ as `python3` on `PATH`
-   Supported shells
    -   bash - first class support
    -   zsh - first class support
    -   fish - community supported
    -   tcsh - community supported
-   Supported platforms
    -   macOS
-   Supported installation methods
    -   source code - first class support
    -   Homebrew / MacPorts - community supported

Due to limited time and resources, only "first class support" items will
be maintained by the primary committers. All "community supported" items
will be updated based on pull requests submitted by the general public.

Please continue opening issues and providing feedback for community
supported items since consolidating information helps other users
troubleshoot and submit enhancements and fixes.

### MANUAL

Grab a copy of autojump:

    git clone https://github.com/wting/autojump.git

Run the installation script and follow on screen instructions.

    cd autojump
    ./install.py or ./uninstall.py

### AUTOMATIC

#### macOS

Homebrew is the recommended installation method for macOS:

    brew install autojump

MacPorts is also available:

    port install autojump

KNOWN ISSUES
------------

-   autojump does not support directories that begin with `-`.

-   For bash users, autojump keeps track of directories by modifying
    `$PROMPT_COMMAND`. Do not overwrite `$PROMPT_COMMAND`:

        export PROMPT_COMMAND="history -a"

    Instead append to the end of the existing \$PROMPT\_COMMAND:

        export PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND ;} history -a"

REPORTING BUGS
--------------

For any questions or issues please visit:

    https://github.com/wting/autojump/issues

AUTHORS
-------

autojump was originally written by Joël Schaerer, and currently
maintained by William Ting. More contributors can be found in `AUTHORS`.

COPYRIGHT
---------

Copyright © 2016 Free Software Foundation, Inc. License GPLv3+: GNU GPL
version 3 or later <http://gnu.org/licenses/gpl.html>. This is free
software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.
