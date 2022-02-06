#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from ..util import (
    ABCObject,
    StringCompat,
    StringifiedComparisons,
    FillMissingComparisons,
)


class PMPackageKey(ABCObject, StringCompat):
    """
    A base class for a package key (CP/qualified package name).
    """

    def __new__(self, key):
        """
        Instantiate.

        @param key: complete package key
        @type key: string
        """
        return StringCompat.__new__(self, key)

    @abstractproperty
    def category(self):
        """
        The package category.

        @type: string/C{None}
        """
        pass

    @abstractproperty
    def package(self):
        """
        The package name.

        @type: string
        """
        pass


class PMIncompletePackageKey(PMPackageKey):
    """
    An incomplete package key (without a category).

    This is just a helper class to simplify implementations. You should not
    rely on this particular class being used, implementations are free to
    implement incomplete keys using plain L{PMPackageKey}.
    """

    @property
    def category(self):
        return None

    @property
    def package(self):
        return str(self)


class PMPackageVersion(ABCObject, FillMissingComparisons, StringCompat):
    """
    A base class for a package version.
    """

    def __new__(self, ver):
        """
        Instantiate.

        @param ver: complete package version
        @type ver: string
        """
        return StringCompat.__new__(self, ver)

    @abstractproperty
    def without_revision(self):
        """
        The actual package version.

        @type: string
        """
        pass

    @abstractproperty
    def revision(self):
        """
        The ebuild revision.

        @type: int
        """
        pass

    @abstractmethod
    def __lt__(self, other):
        pass


class PMAtom(ABCObject, StringifiedComparisons):
    """
    A base class for PM-specific atom (dependency specification).
    """

    @abstractmethod
    def __init__(self, s):
        """
        Create a new atom from string.

        @param s: atom-formatted string
        @type s: string
        """
        pass

    @abstractmethod
    def __contains__(self, pkg):
        """
        Check whether a package is contained in the set of packages matched
        by the atom.

        Please note that with blockers, this function returns C{True} for all
        atoms not blocked by the atom.

        @param pkg: a package to match
        @type pkg: L{PMPackage}
        """
        pass

    @abstractmethod
    def __str__(self):
        """
        Return the string representation of the atom.

        If the atom is incomplete (misses a category), the result is undefined.
        It can raise an exception then.
        """
        pass

    def __repr__(self):
        if self.complete:
            s = repr(str(self))
        else:
            s = "<incomplete>"
        return "%s(%s)" % (self.__class__.__name__, s)

    @abstractproperty
    def complete(self):
        """
        Whether the atom is complete, i.e. whether the category is specified.

        If an atom is incomplete, it is impossible to stringify it. Using such
        an atom with L{pkgset.PMPackageSet.select()} may result
        in an L{AmbiguousPackageSetError}.

        @type: bool
        """
        pass

    @abstractproperty
    def blocking(self):
        """
        Whether the atom represents a blocking atom.

        Support for block atoms is limited. They may not be parseable from user
        input (using L{PackageManager.Atom()}), and they should not be used as
        arguments to matching functions.

        @type: bool
        """
        pass

    @abstractproperty
    def key(self):
        """
        The package key.

        @type: L{PMPackageKey}
        """
        pass

    @abstractproperty
    def version(self):
        """
        The package version.

        @type: L{PMPackageVersion}/C{None}
        """
        pass

    @abstractproperty
    def slot(self):
        """
        The package slot (without subslot, if specified).

        @type: string/C{None}
        """
        pass

    @abstractproperty
    def subslot(self):
        """
        The package subslot restriction (if specified).

        @type: string/C{None}
        """
        pass

    @abstractproperty
    def slot_operator(self):
        """
        The package slot operator (None, '=' or '*').

        @type: string/C{None}
        """
        pass

    @abstractproperty
    def repository(self):
        """
        The package repository name (if specified).

        @type: string/C{None}
        """
        pass
