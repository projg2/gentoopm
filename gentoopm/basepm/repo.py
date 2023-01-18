#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011-2023 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os
import os.path
import typing

from pathlib import Path

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


class GlobalUseFlag(typing.NamedTuple):
    """Global USE flag (as defined by use.desc)"""

    name: str
    description: typing.Optional[str] = None


class UseExpand(typing.NamedTuple):
    """USE_EXPAND group"""

    name: str
    prefixed: bool
    visible: bool
    values: dict[str, GlobalUseFlag]

    @property
    def prefixed_values(self) -> dict[str, GlobalUseFlag]:
        return {
            f"{self.name.lower()}_{flag}":
            GlobalUseFlag(f"{self.name.lower()}_{flag}",
                          details.description)
            for flag, details in self.values.items()
        }


class ArchDesc(typing.NamedTuple):
    """Architecture defined by arch.list + arches.desc"""

    name: str
    stability: typing.Optional[str] = None


class LicenseDesc(typing.NamedTuple):
    """License information"""

    name: str


class LicenseGroup(typing.NamedTuple):
    """License group"""

    name: str
    nested_groups: list[str]
    licenses: list[str]


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

    @property
    def global_use(self) -> dict[str, GlobalUseFlag]:
        """Get dict of global USE flags as defined in use.desc"""

        # Portage does not implement use.desc support, so we roll out
        # a generic implementation here
        try:
            with open(Path(self.path) / "profiles/use.desc", "r") as f:
                def inner() -> typing.Generator[tuple[str, str], None, None]:
                    for line in f:
                        line = line.strip()
                        if not line or line[0] == "#":
                            continue
                        name, desc = line.split(" - ", 1)
                        yield (name, desc)
                return {
                    name: GlobalUseFlag(name, desc) for name, desc in inner()
                }

        except FileNotFoundError:
            return {}

    def _use_expand_desc(self, k: str) -> dict[str, GlobalUseFlag]:
        """Read USE_EXPAND descriptions for given key"""

        filename = k.lower() + ".desc"
        try:
            with open(Path(self.path) / "profiles/desc" / filename, "r") as f:
                def inner() -> typing.Generator[tuple[str, str], None, None]:
                    for line in f:
                        line = line.strip()
                        if not line or line[0] == "#":
                            continue
                        name, desc = line.split(" - ", 1)
                        yield (name, desc)
                return {
                    name: GlobalUseFlag(name, desc) for name, desc in inner()
                }

        except FileNotFoundError:
            return {}

    @abstractproperty
    def use_expand(self) -> dict[str, UseExpand]:
        """Get dict of USE_EXPAND groups"""

    @property
    def arches(self) -> dict[str, ArchDesc]:
        """Get dict of known architectures"""

        arches = {}

        try:
            with open(Path(self.path) / "profiles/arch.list", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and line[0] != "#":
                        arches[line] = ArchDesc(line)
        except FileNotFoundError:
            pass

        try:
            with open(Path(self.path) / "profiles/arches.desc", "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line[0] == "#":
                        continue
                    arch, stability, *_ = line.split()
                    arches[arch] = ArchDesc(name=arch,
                                            stability=stability)
        except FileNotFoundError:
            pass

        return arches

    @property
    def licenses(self) -> dict[str, LicenseDesc]:
        try:
            return {
                name: LicenseDesc(name) for name
                in os.listdir(Path(self.path) / "licenses")
                if not name.startswith(".")
            }
        except FileNotFoundError:
            return {}

    @property
    def license_groups(self) -> dict[str, LicenseGroup]:
        """Get dict of license groups"""
        def inner(f: typing.IO[str],
                  ) -> typing.Generator[tuple[str, LicenseGroup], None, None]:
            for line in f:
                line = line.strip()
                if not line or line[0] == "#":
                    continue

                group, *members = line.split()
                yield (group,
                       LicenseGroup(name=group,
                                    nested_groups=[member[1:] for member
                                                   in members
                                                   if member.startswith("@")],
                                    licenses=[member for member in members
                                              if not member.startswith("@")]))

        try:
            with open(Path(self.path) / "profiles/license_groups", "r") as f:
                return dict(inner(f))
        except FileNotFoundError:
            return {}

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
