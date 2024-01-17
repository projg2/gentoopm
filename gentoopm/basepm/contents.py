# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

import os.path
from abc import abstractmethod

from ..util import ABCObject, StringCompat


class PMContentObj(StringCompat):
    def __new__(self, path):
        return StringCompat.__new__(self, os.path.normpath(path))


class PMPackageContents(ABCObject):
    """
    A base class for package contents (files installed by a package).
    """

    @abstractmethod
    def __iter__(self):
        """
        Iterate over files and directories installed by the package.
        """
        pass

    def __contains__(self, path):
        """
        Check whether the path given is installed by the package.

        @param path: the path to check
        @type path: string
        @return: whether the path exists in package contents
        @rtype: bool
        """

        path = os.path.normpath(path)
        for f in self:
            if str(f) == path:
                return True
        return False
