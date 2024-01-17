# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

from abc import abstractmethod
import atexit

from ..util import ABCObject


class BashParser(ABCObject):
    """
    A base class for bash script parsing facility.
    """

    @abstractmethod
    def load_file(self, f):
        """
        Load and execute the contents of file.

        @param f: the file to execute
        @type f: file
        """
        pass

    @abstractmethod
    def __getitem__(self, k):
        """
        Get the value of an environment variable.

        @param k: environment variable name
        @type k: string
        @return: value of the environment variable (or C{''} if unset)
        @rtype: string
        """
        pass

    def copy(self, *varlist):
        """
        Get values of multiple environment variables, and return them
        as a dict (a 'local copy' of the environment).

        @param varlist: environment variable names
        @type varlist: list(string)
        @return: environment variables with values
        @rtype: dict(string -> string)
        """

        out = {}
        for v in varlist:
            out[v] = self[v]
        return out


def get_any_bashparser():
    """
    Get any BashParser implementation (the best one available).

    @return: a BashParser instance
    @rtype: L{BashParser}
    """
    from gentoopm.bash.bashserver import BashServer

    s = BashServer()
    atexit.register(s.terminate)
    return s
