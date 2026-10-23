## INSTALLATION

### REQUIREMENTS

- Python v3.15+ as `python3` on `PATH`
- Supported shells
    - bash  - first class support
    - zsh - first class support
    - fish - community supported
    - tcsh - community supported
- Supported platforms
    - macOS
- Supported installation methods
    - source code - first class support
    - Homebrew / MacPorts - community supported

Due to limited time and resources, only "first class support" items will be
maintained by the primary committers. All "community supported" items will be
updated based on pull requests submitted by the general public.

Please continue opening issues and providing feedback for community supported
items since consolidating information helps other users troubleshoot and submit
enhancements and fixes.

### MANUAL

Grab a copy of autojump:

    git clone git://github.com/wting/autojump.git

Run the installation script and follow on screen instructions.

    cd autojump
    ./install.py or ./uninstall.py

### AUTOMATIC

#### macOS

Homebrew is the recommended installation method for macOS:

    brew install autojump

MacPorts is also available:

    port install autojump
