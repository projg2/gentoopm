#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty
import os

from ..util import ABCObject

from .stack import PMRepoStackWrapper


class PackageManager(ABCObject):
    """
    Base abstract class for a package manager.
    """

    config_root = ""

    @abstractproperty
    def name(self):
        """
        Return the canonical name of the PM. The value should be static
        and unique.

        @type: string
        """
        pass

    @abstractproperty
    def version(self):
        """
        Return the PM version as a simple string.

        @type: string
        """
        pass

    @abstractmethod
    def reload_config(self):
        """
        (Re-)load the configuration of a particular package manager. Set up
        internal variables.

        Called by default L{__init__()}.
        """
        pass

    def __init__(self, config_root=""):
        """
        Initialize the new package manager instance.

        @param config_root: Configuration root location
        @type config_root: string
        """
        self.config_root = config_root or os.environ.get("PORTAGE_CONFIGROOT", "")
        self.reload_config()

    @abstractproperty
    def repositories(self):
        """
        Currently enabled ebuild repositories.

        @type: L{PMRepositoryDict}
        """
        pass

    @abstractproperty
    def root(self):
        """
        The root path as specified by current PM configuration.

        @type: str
        """
        pass

    @abstractproperty
    def installed(self):
        """
        Repository with installed packages (vardb).

        @type: L{PMRepository}
        """
        pass

    @property
    def stack(self):
        """
        Return a PMRepository providing access to the stacked packages in all
        ebuild repositories. It returns packages from all the repos.

        @type: L{PMRepoStackWrapper}
        """
        return PMRepoStackWrapper(self.repositories)

    @abstractproperty
    def Atom(self):
        """
        The PM-specific atom class.

        @type: L{PMAtom}
        """
        pass

    @abstractproperty
    def config(self):
        """
        The PM config instance.

        @type: L{PMConfig}
        """
        pass
