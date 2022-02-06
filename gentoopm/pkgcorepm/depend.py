#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.ebuild.atom import atom
from pkgcore.restrictions.boolean import (
    OrRestriction,
    AndRestriction,
    JustOneRestriction,
    AtMostOneOfRestriction,
)
from pkgcore.restrictions.packages import Conditional
from pkgcore.restrictions.values import ContainmentMatch

from ..basepm.depend import (
    PMPackageDepSet,
    PMConditionalDep,
    PMAnyOfDep,
    PMAllOfDep,
    PMExactlyOneOfDep,
    PMAtMostOneOfDep,
    PMBaseDep,
    PMRequiredUseAtom,
)

from .atom import PkgCoreAtom


class PkgCoreBaseDep(PMBaseDep):
    def __init__(self, deps, pkg):
        self._deps = deps
        self._pkg = pkg

    def __iter__(self):
        for d in self._deps:
            if isinstance(d, atom):
                yield PkgCoreAtom(d)
            elif isinstance(d, ContainmentMatch):  # REQUIRED_USE
                assert len(d.vals) == 1
                yield PMRequiredUseAtom(next(iter(d.vals)))
            elif isinstance(d, OrRestriction):
                yield PkgCoreAnyOfDep(d, self._pkg)
            elif isinstance(d, AndRestriction):
                yield PkgCoreAllOfDep(d, self._pkg)
            elif isinstance(d, JustOneRestriction):
                yield PkgCoreExactlyOneOfDep(d, self._pkg)
            elif isinstance(d, AtMostOneOfRestriction):
                yield PkgCoreAtMostOneOfDep(d, self._pkg)
            elif isinstance(d, Conditional) and d.attr == "use":
                yield PkgCoreConditionalUseDep(d, self._pkg)
            else:
                raise NotImplementedError("Parsing %s not implemented" % repr(d))


class PkgCoreAnyOfDep(PMAnyOfDep, PkgCoreBaseDep):
    pass


class PkgCoreAllOfDep(PMAllOfDep, PkgCoreBaseDep):
    pass


class PkgCoreExactlyOneOfDep(PMExactlyOneOfDep, PkgCoreBaseDep):
    pass


class PkgCoreAtMostOneOfDep(PMAtMostOneOfDep, PkgCoreBaseDep):
    pass


class PkgCoreConditionalUseDep(PMConditionalDep, PkgCoreBaseDep):
    @property
    def enabled(self):
        return self._deps.restriction.match(self._pkg.use)


class PkgCorePackageDepSet(PMPackageDepSet, PkgCoreAllOfDep):
    @property
    def without_conditionals(self):
        return PkgCoreUncondAllOfDep(self._deps.evaluate_depset(self._pkg.use))


class PkgCoreUncondDep(PkgCoreBaseDep):
    def __init__(self, deps):
        self._deps = deps

    @property
    def without_conditionals(self):
        return self

    def __iter__(self):
        for d in self._deps:
            if isinstance(d, atom):
                yield PkgCoreAtom(d)
            elif isinstance(d, OrRestriction):
                yield PkgCoreUncondAnyOfDep(d)
            elif isinstance(d, AndRestriction):
                yield PkgCoreUncondAllOfDep(d, self._pkg)
            elif isinstance(d, JustOneRestriction):
                yield PkgCoreUncondExactlyOneOfDep(d, self._pkg)
            elif isinstance(d, AtMostOneOfRestriction):
                yield PkgCoreUncondAtMostOneOfDep(d, self._pkg)
            else:
                raise NotImplementedError("Parsing %s not implemented" % repr(d))


class PkgCoreUncondAnyOfDep(PMAnyOfDep, PkgCoreUncondDep):
    pass


class PkgCoreUncondAllOfDep(PMAllOfDep, PkgCoreUncondDep):
    pass


class PkgCoreUncondAllOfDep(PMExactlyOneOfDep, PkgCoreUncondDep):
    pass


class PkgCoreUncondAllOfDep(PMAtMostOneOfDep, PkgCoreUncondDep):
    pass
