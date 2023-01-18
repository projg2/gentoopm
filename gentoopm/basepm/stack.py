#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from .repo import (PMRepository, GlobalUseFlag, UseExpand, ArchDesc,
                   LicenseDesc, LicenseGroup,
                   )
from .pkgset import PMPackageSet


class PMRepoStackWrapper(PMRepository):
    """
    A wrapper class providing access to all packages in all repositories.
    """

    def __init__(self, repos):
        self._repos = repos

    def __iter__(self):
        for r in self._repos:
            for p in r:
                yield p

    def filter(self, *args, **kwargs):
        return PMFilteredStackPackageSet(self._repos, args, kwargs)

    @property
    def global_use(self) -> dict[str, GlobalUseFlag]:
        """Get dict of global USE flags as defined in use.desc"""
        ret = {}
        for r in self._repos:
            ret.update(r.global_use)
        return ret

    @property
    def use_expand(self) -> dict[str, UseExpand]:
        """Get dict of USE_EXPAND groups"""
        ret = {}
        for r in self._repos:
            ret.update(r.use_expand)
        return ret

    @property
    def arches(self) -> dict[str, ArchDesc]:
        """Get dict of known architectures"""
        ret = {}
        for r in self._repos:
            ret.update(r.arches)
        return ret

    @property
    def licenses(self) -> dict[str, LicenseDesc]:
        """Get dict of known licenses"""
        ret = {}
        for r in self._repos:
            ret.update(r.licenses)
        return ret

    @property
    def license_groups(self) -> dict[str, LicenseGroup]:
        """Get dict of license groups"""
        ret = {}
        for r in self._repos:
            ret.update(r.license_groups)
        return ret


class PMFilteredStackPackageSet(PMPackageSet):
    """
    A wrapper class providing access to filtering packages in all repositories.
    Thanks to it, per-repo filter optimizations can be performed.
    """

    def __init__(self, repos, args, kwargs, addkwargs=[]):
        self._repos = repos
        self._args = args
        self._kwargs = kwargs
        # keywords may overlap, so only optimize the first set
        self._addkwargs = addkwargs

    def __iter__(self):
        for r in self._repos:
            for p in r.filter(*self._args, **self._kwargs):
                for kw in self._addkwargs:
                    if not p._matches(**kw):
                        break
                else:
                    yield p

    def filter(self, *args, **kwargs):
        return PMFilteredStackPackageSet(
            self._repos, self._args + args, self._kwargs, self._addkwargs + [kwargs]
        )
