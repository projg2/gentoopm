#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import bz2

from ..bash import get_any_bashparser


def _load_bp(bp, path):
    """
    Load a file onto a bash parser.

    @param bp: the bash parser instance
    @type bp: L{BashParser}
    @param path: path to the environment file
    @type path: string
    """

    def _try_file(t):
        f = t(path, "rb")
        try:
            bp.load_file(f)
        finally:
            f.close()

    try:
        _try_file(bz2.BZ2File)
    except IOError:
        _try_file(open)


class LazyBashParser(object):
    """
    Lazily-initialized, shared bash parser wrapper.
    """

    _curr_path = None
    _parser = None

    def set_file(self, path):
        """
        Switch the currently used environment file, if necessary.

        @param path: path to the new environment file
        @type path: string
        """

        if self._curr_path == path:
            return
        self._curr_path = path
        if self._parser is None:
            self._parser = get_any_bashparser()
        try:
            _load_bp(self._parser, path)
        except Exception as e:
            try:
                self._parser.terminate()
            except:
                pass
            self._parser = None
            raise e

    def __getitem__(self, k):
        return self._parser[k]

    def __call__(self, code):
        return self._parser(code)

    def copy(self, *v):
        return self._parser.copy(*v)


_bp = LazyBashParser()


class PMPackageEnvironment(object):
    """
    Package environment accessor class.
    """

    def __init__(self, path):
        """
        Instantiate L{PMPackageEnvironment} accessor.

        @param path: path to the environment file
        @type path: string
        """
        self._path = path

    def __getitem__(self, k):
        """
        Get the value of an environment key by name.

        @param k: the key to access
        @type k: string
        @return: the environment variable value
        @rtype: string
        """
        _bp.set_file(self._path)
        return _bp[k]

    def __call__(self, code):
        """
        Run the given bash code and return the exit code.

        @param code: bash code to run
        @type code: string
        @return: the return value (exit code)
        @rtype: integer
        """
        _bp.set_file(self._path)
        return _bp(code)

    def copy(self, *keys):
        """
        Get a number of environment keys as a dict.

        @param keys: keys to access
        @type keys: strings
        @return: a dict of copied environment keys
        @rtype: dict(string -> string)
        """
        _bp.set_file(self._path)
        return _bp.copy(*keys)

    def fork(self):
        """
        Fork the bash parser. In other words, return a completely separate
        instance with the environment file loaded.

        @return: forked L{BashParser} instance
        @rtype: L{BashParser}
        """
        bp = get_any_bashparser()
        _load_bp(bp, self._path)
        return bp
