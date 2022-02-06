#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from .repo import PMRepository
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
