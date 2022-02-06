#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractmethod, abstractproperty

from ..util import (
    ABCObject,
    FillMissingComparisons,
    StringCompat,
    EnumTuple,
    FillMissingNotEqual,
)

from .atom import PMAtom, PMPackageKey
from .environ import PMPackageEnvironment

PMPackageState = EnumTuple("PMPackageState", "installable", "installed")


class PMBoundPackageKey(FillMissingNotEqual, PMPackageKey):
    """
    A package key bound to a specific package.
    """

    @abstractproperty
    def state(self):
        """
        State of the bound package.

        @type: L{PMPackageState}
        """
        pass

    def __eq__(self, other):
        if isinstance(other, PMBoundPackageKey) and not self.state == other.state:
            return False
        return PMPackageKey.__eq__(self, other)

    def __hash__(self):
        return hash((str(self), self.state))


class PMPackageDescription(ABCObject):
    """
    Description of a package.
    """

    @abstractproperty
    def short(self):
        """
        The short package description (e.g. C{DESCRIPTION} within the ebuild).

        @type: string
        """
        pass

    @abstractproperty
    def long(self):
        """
        The long package description (e.g. from C{metadata.xml}).

        @type: string/C{None}
        """
        pass


class PMUseFlag(ABCObject, StringCompat):
    """
    A base class for a USE flag supported by a package.
    """

    def __new__(self, usestr):
        """
        Instantiate from an IUSE atom.

        @param usestr: the IUSE atom (C{[+-]?flag})
        @type usestr: string
        """
        return StringCompat.__new__(self, usestr.lstrip("+-"))

    @property
    def name(self):
        """
        The flag name.

        @type: string
        """
        return str(self)

    @abstractproperty
    def enabled(self):
        """
        Whether the flag is enabled.

        @type: bool
        """
        pass


class PMPackageMaintainer(ABCObject, StringCompat):
    """
    A base class for a package maintainer.
    """

    def __new__(self, email, name=None):
        """
        Instantiate the actual string. Requires other props prepared
        beforehand.

        @param email: maintainer's e-mail address
        @type email: string
        @param name: maintainer's real name
        @type name: string/C{None}
        """

        ret = ["<%s>" % email]
        if name is not None:
            ret.insert(0, name)

        ret = StringCompat.__new__(self, " ".join(ret))
        ret._name = name
        ret._email = email
        return ret

    @property
    def name(self):
        """
        Maintainer's real name.

        @type: string/C{None}
        """
        return self._name

    @property
    def email(self):
        """
        Maintainer's e-mail address.

        @type: string
        """
        return self._email

    @abstractproperty
    def description(self):
        """
        Detailed maintainership description.

        @type: string/C{None}
        """
        pass


class PMPackage(PMAtom, FillMissingComparisons):
    """
    An abstract class representing a single, uniquely-identified package
    in the package tree.
    """

    def _matches(self, *args):
        """
        Check whether the package matches passed filters. Please note that this
        method may not be called at all if PM is capable of a more efficient
        filtering.

        @param args: list of package matchers
        @type args: list(L{PMPackageMatcher},L{PMAtom})
        @return: True if package matches
        @rtype: bool
        @raise KeyError: when invalid metadata key is referenced in kwargs
        @todo: keyword matchers not yet re-defined for new metadata API.
        """

        for f in args:
            if isinstance(f, PMAtom):  # an atom
                if not self in f:
                    return False
            elif hasattr(f, "__call__"):
                if not f(self):
                    return False
            else:
                raise ValueError("Incorrect positional argument: %s" % f)

        return True

    @abstractproperty
    def path(self):
        """
        Path to the ebuild file (or vardb entry) if appropriate.

        This function may return C{None} if that information is not available
        or the particular repository doesn't operate on local filesystem.

        @type: string/C{None}
        """
        pass

    @abstractproperty
    def eapi(self):
        """
        The EAPI used by the ebuild.

        @type: string
        """
        pass

    @abstractproperty
    def description(self):
        """
        The description of the package.

        @type: L{PMPackageDescription}
        """
        pass

    @abstractproperty
    def inherits(self):
        """
        Eclasses inherited by a package.

        @type: L{SpaceSepFrozenSet}
        """
        pass

    @abstractproperty
    def defined_phases(self):
        """
        List of phase functions declared by a package, if available.
        C{None} otherwise. Empty L{SpaceSepFrozenSet} means no phase function
        is declared.

        @type: L{SpaceSepFrozenSet}/C{None}
        """
        pass

    @abstractproperty
    def homepages(self):
        """
        Homepages of a package.

        @type: L{SpaceSepTuple}
        """
        pass

    @abstractproperty
    def keywords(self):
        """
        Package keywords.

        @type: L{SpaceSepFrozenSet}
        """
        pass

    @property
    def environ(self):
        """
        The environment accessor object for the package.

        Please note that this function may return C{None} if environment is
        inaccessible (path is unavailable or file does not exist).

        @type: L{PMPackageEnvironment}/C{None}
        """

        p = self.path
        if p is None:
            return None

        if os.path.isdir(p):

            def _mtime_if_exists(path):
                try:
                    return os.path.getmtime(path)
                except OSError:
                    return -1

            files = [os.path.join(p, fn) for fn in ("environment.bz2", "environment")]
            # Take the newer one.
            p = sorted(files, key=_mtime_if_exists, reverse=True)[0]

        if not os.path.exists(p):
            return None
        return PMPackageEnvironment(p)

    @abstractproperty
    def build_dependencies(self):
        """
        Get the package build dependencies (C{DEPEND}).

        @type: L{PMPackageDepSet}
        """
        pass

    @abstractproperty
    def cbuild_build_dependencies(self):
        """
        Get the package CBUILD build dependencies (C{BDEPEND}).
        Equivalent to build_dependencies on EAPIs not supporting BDEPEND.

        @type: L{PMPackageDepSet}
        """
        pass

    @abstractproperty
    def run_dependencies(self):
        """
        Get the package runtime dependencies (C{RDEPEND}).

        @type: L{PMPackageDepSet}
        """
        pass

    @abstractproperty
    def post_dependencies(self):
        """
        Get the package post-installed dependencies (C{PDEPEND}).

        @type: L{PMPackageDepSet}
        """
        pass

    @abstractproperty
    def use(self):
        """
        Get the list of USE flags applying to the ebuild. Iterating over the
        list should return only the explicitly listed flags (C{IUSE}), though
        it is also possible to explicitly get other flags (using indexing)
        applying to the ebuild.

        @type: L{SpaceSepFrozenSet}(L{PMUseFlag})
        """
        pass

    @abstractproperty
    def required_use(self):
        """
        Get the C{REQUIRED_USE} specification.

        @type: L{PMPackageDepSet}
        """
        pass

    @abstractproperty
    def slotted_atom(self):
        """
        Return an atom matching all packages in the same slot as the package.

        @type: L{PMAtom}
        """
        pass

    @abstractproperty
    def unversioned_atom(self):
        """
        Return an atom matching all packages with the same key as the package.

        @type: L{PMAtom}
        """
        pass

    @abstractmethod
    def __lt__(self, other):
        pass

    # atom API

    def __contains__(self, pkg):
        return self == pkg

    @property
    def complete(self):
        return True

    @property
    def blocking(self):
        return False


class PMInstallablePackage(PMPackage):
    """
    An abstract class for a package which can be installed.
    """

    @abstractproperty
    def maintainers(self):
        """
        Get the package maintainer list (or C{None} if unavailable).

        @type: tuple(L{PMPackageMaintainer})/C{None}
        """
        pass

    @abstractproperty
    def repo_masked(self):
        """
        Return True if package is masked in repository's package.mask.
        """
        pass


class PMInstalledPackage(PMPackage):
    """
    An abstract class for a installed package.
    """

    @abstractproperty
    def contents(self):
        """
        Return package contents list accessor.

        @type: L{PMPackageContents}
        """
        pass
