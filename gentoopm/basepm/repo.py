#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractmethod, abstractproperty

from ..util import ABCObject, FillMissingComparisons

from .pkgset import PMPackageSet


class PMRepositoryDict(ABCObject):
    """
    A dict-like object providing access to a set of repositories.

    The repositories can be referenced through their names or paths,
    or iterated over. An access should result in an instantiated PMRepository
    subclass.
    """

    def __getitem__(self, key):
        """
        Get the repository by its name or path. If using a path as a key,
        an absolute path must be passed.

        By default, iterates over the repository list. Can be replaced with
        something more optimal.

        @param key: repository name or path
        @type key: string
        @return: matching repository
        @rtype: L{PMEbuildRepository}
        @raise KeyError: when no repository matches the key
        """
        bypath = os.path.isabs(key)

        for r in self:
            if bypath:
                # We're requiring exact match to match portage behaviour
                m = r.path == key
            else:
                m = r.name == key
            if m:
                return r
        raise KeyError("No repository matched key %s" % key)

    def __contains__(self, k):
        try:
            self[k]
        except KeyError:
            return False
        else:
            return True

    @abstractmethod
    def __iter__(self):
        """
        Iterate over the repository list.

        @return: iterator over repositories
        @rtype: iter(L{PMEbuildRepository})
        """
        pass

    def __repr__(self):
        return "%s([\n%s])" % (
            self.__class__.__name__,
            ",\n".join(["\t%s" % repr(x) for x in self]),
        )


class PMRepository(PMPackageSet):
    """
    Base abstract class for a single repository.
    """


class PMEbuildRepository(PMRepository, FillMissingComparisons):
    """
    Base abstract class for an ebuild repository (on livefs).
    """

    @abstractproperty
    def name(self):
        """
        Return the repository name (either from the repo_name file or PM
        fallback name).

        @type: string
        """
        pass

    @abstractproperty
    def path(self):
        """
        Return the canonical path to the ebuild repository.

        @type: string
        """
        pass

    @abstractmethod
    def __lt__(self, other):
        pass

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.path == other.path

    def __hash__(self):
        return hash((self.name, self.path))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, repr(self.name))
