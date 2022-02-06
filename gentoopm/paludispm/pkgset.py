#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from ..exceptions import EmptyPackageSetError, AmbiguousPackageSetError

from .atom import PaludisAtom


class PaludisPackageSet(object):
    def __init__(self, env):
        self._env = env

    def filter(self, *args, **kwargs):
        newargs = [(a if not isinstance(a, str) else PaludisAtom(a)) for a in args]

        return PaludisFilteredPackageSet(self, newargs, kwargs)


class PaludisFilteredPackageSet(PaludisPackageSet, PMFilteredPackageSet):
    def __init__(self, pset, args, kwargs):
        PaludisPackageSet.__init__(self, pset._env)
        PMFilteredPackageSet.__init__(self, pset, args, kwargs)
