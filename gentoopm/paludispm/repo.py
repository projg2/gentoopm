#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractproperty

import paludis

from ..basepm.repo import PMRepository, PMRepositoryDict, PMEbuildRepository

from .atom import PaludisAtom
from .pkg import PaludisInstallableID, PaludisInstalledID
from .pkgset import PaludisPackageSet


class PaludisRepoDict(PMRepositoryDict):
    def __iter__(self):
        for r in self._env.repositories:
            if r.format_key().parse_value() == "e":
                yield PaludisLivefsRepository(r, self._env)

    def __init__(self, env):
        self._env = env


class PaludisEnumID(object):
    pass


class PaludisBaseRepo(PMRepository, PaludisPackageSet):
    @property
    def _gen(self):
        return paludis.Generator.All()

    @property
    def _filt(self):
        return paludis.Filter.All()

    @property
    def _sel(self):
        return paludis.Selection.AllVersionsUnsorted

    @abstractproperty
    def _pkg_class(self):
        pass

    def __iter__(self):
        enum = PaludisEnumID()
        for p in self._env[self._sel(paludis.FilteredGenerator(self._gen, self._filt))]:
            yield self._pkg_class(p, self._env)

    def filter(self, *args, **kwargs):
        pset = self
        newargs = []

        for f in args:
            if isinstance(f, str):
                f = PaludisAtom(f, self._env)
            if isinstance(f, PaludisAtom):
                newgen = paludis.Generator.Matches(
                    f._atom, paludis.MatchPackageOptions()
                )
                pset = PaludisOverrideRepo(pset, gen=newgen)
            else:
                newargs.append(f)

        if id(pset) == id(self):
            return PaludisPackageSet.filter(self, *args, **kwargs)
        elif newargs or kwargs:
            return pset.filter(*newargs, **kwargs)
        else:
            return pset

    @property
    def sorted(self):
        return PaludisOverrideRepo(self, sel=paludis.Selection.AllVersionsSorted)


class PaludisOverrideRepo(PaludisBaseRepo):
    @property
    def _gen(self):
        return self._mygen

    @property
    def _filt(self):
        return self._myfilt

    @property
    def _sel(self):
        return self._mysel

    @property
    def _pkg_class(self):
        return self._mypkg_class

    def __init__(self, repo, filt=None, gen=None, sel=None):
        PaludisBaseRepo.__init__(self, repo._env)
        self._myfilt = filt or repo._filt
        self._mygen = repo._gen
        if gen is not None:
            self._mygen &= gen
        self._mysel = sel or repo._sel
        self._mypkg_class = repo._pkg_class


class PaludisStackRepo(PaludisBaseRepo):
    _pkg_class = PaludisInstallableID

    @property
    def _filt(self):
        return paludis.Filter.SupportsInstallAction()


class PaludisLivefsRepository(PaludisBaseRepo, PMEbuildRepository):
    _pkg_class = PaludisInstallableID

    def __init__(self, repo_obj, env):
        PaludisBaseRepo.__init__(self, env)
        self._repo = repo_obj

    @property
    def _gen(self):
        return paludis.Generator.InRepository(self._repo.name)

    @property
    def name(self):
        return str(self._repo.name)

    @property
    def path(self):
        return self._repo.location_key().parse_value()

    def __lt__(self, other):
        return self._env.more_important_than(other.name, self.name)


class PaludisInstalledRepo(PaludisBaseRepo):
    _pkg_class = PaludisInstalledID

    def __init__(self, env, root):
        PaludisBaseRepo.__init__(self, env)
        self._root = root

    @property
    def _filt(self):
        return paludis.Filter.InstalledAtRoot(self._root)
