# Albert Launcher Unicode Extension
Finds Unicode.

Dependencies:

- [uni](https://github.com/arp242/uni)

## Install
To install, copy or symlink this directory to `~/.local/share/albert/python/plugins/unicode/`.

## Development Setup
To setup the project for development, run:

    $ cd unicode/
    $ pre-commit install --hook-type pre-commit --hook-type commit-msg
    $ mkdir --parents typings/albert/
    $ ln --symbolic ~/.local/share/albert/python/plugins/albert.pyi typings/albert/__init__.pyi

To lint and format files, run:

    $ pre-commit run --all-files
