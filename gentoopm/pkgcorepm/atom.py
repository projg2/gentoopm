#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.ebuild.atom import atom
from pkgcore.ebuild.restricts import (
    PackageDep,
    VersionMatch,
    RepositoryDep,
    SlotDep,
    SubSlotDep,
)
from pkgcore.restrictions.boolean import AndRestriction
from pkgcore.util.parserestrict import parse_match, ParseError

from ..basepm.atom import PMAtom, PMPackageKey, PMPackageVersion, PMIncompletePackageKey
from ..exceptions import InvalidAtomStringError


def _find_res(res, cls):
    if isinstance(res, AndRestriction):
        restrictions = res.restrictions
    else:
        restrictions = (res,)

    for r in restrictions:
        if isinstance(r, cls):
            return r
    else:
        return None


class PkgCorePackageKey(PMPackageKey):
    def __new__(self, atom):
        return PMPackageKey.__new__(self, atom.key)

    def __init__(self, atom):
        self._atom = atom

    @property
    def category(self):
        return self._atom.category

    @property
    def package(self):
        return self._atom.package


class PkgCoreIncompletePackageKey(PMIncompletePackageKey):
    def __new__(self, r):
        pd = _find_res(r, PackageDep)
        if pd is None:
            raise AssertionError("No PackageDep in restrictions.")
        return PMIncompletePackageKey.__new__(self, pd.restriction.exact)


class PkgCorePackageVersion(PMPackageVersion):
    def __new__(self, atom):
        if atom.version is None:
            raise AssertionError("Empty version in atom")
        return PMPackageVersion.__new__(self, atom.fullver)

    def __init__(self, atom):
        self._atom = atom

    @property
    def without_revision(self):
        return self._atom.version

    @property
    def revision(self):
        return self._atom.revision or 0

    def __lt__(self, other):
        if self._atom.key != other._atom.key:
            raise NotImplementedError("Unable to compare versions of distinct packages")
        return self._atom < other._atom


class PkgCoreIncompletePackageVersion(PMPackageVersion):
    def __new__(self, r):
        vm = _find_res(r, VersionMatch)
        if vm is None:
            raise AssertionError("No VersionMatch in restrictions.")
        v = PMPackageVersion.__new__(self, str(vm).split()[-1])  # XXX
        try:
            v._r = vm.restriction
        except AttributeError:
            v._r = vm
        return v

    @property
    def without_revision(self):
        return self._r.ver

    @property
    def revision(self):
        return self._r.rev or 0

    def __lt__(self, other):
        raise NotImplementedError("Unable to compare versions of incomplete atoms")


class PkgCoreAtom(PMAtom):
    def __init__(self, s):
        if isinstance(s, atom):
            self._r = s
        else:
            try:
                self._r = parse_match(s)
            except ParseError:
                raise InvalidAtomStringError("Incorrect atom: %s" % s)

    def __contains__(self, pkg):
        return self._r.match(pkg._pkg) != self.blocking

    def __str__(self):
        if self.complete:
            return str(self._r)
        else:
            raise ValueError("Unable to stringify incomplete atom")

    @property
    def complete(self):
        return isinstance(self._r, atom)

    @property
    def blocking(self):
        # incomplete atoms can't block
        return self.complete and self._r.blocks

    @property
    def key(self):
        if self.complete:
            return PkgCorePackageKey(self._r)
        else:
            return PkgCoreIncompletePackageKey(self._r)

    @property
    def version(self):
        try:
            if self.complete:
                return PkgCorePackageVersion(self._r)
            else:
                return PkgCoreIncompletePackageVersion(self._r)
        except AssertionError:
            return None

    @staticmethod
    def strip_slotop(r):
        """Strip slot op from slot/subslot restriction string"""
        if r is None:
            return None
        s = r.restriction.exact
        if s.endswith("=") or s.endswith("*"):
            if len(s) == 1:
                return None
            s = s[:-1]
        return s

    @property
    def slot(self):
        if self.complete:
            return self._r.slot if self._r.slot else None
        else:
            r = _find_res(self._r, SlotDep)
            return self.strip_slotop(r)

    @property
    def subslot(self):
        if self.complete:
            return self._r.subslot if self._r.subslot else None
        else:
            r = _find_res(self._r, SubSlotDep)
            return self.strip_slotop(r)

    @property
    def slot_operator(self):
        if self.complete:
            return self._r.slot_operator if self._r.slot_operator else None
        else:
            # now the fun part -- it's either in SubSlotDep or SlotDep
            r = _find_res(self._r, SubSlotDep)
            if r is None:
                r = _find_res(self._r, SlotDep)
            if r is None:
                return None
            s = r.restriction.exact
            if s.endswith("=") or s.endswith("*"):
                return s[-1]

    @property
    def repository(self):
        if self.complete:
            return self._r.repo_id
        else:
            r = _find_res(self._r, RepositoryDep)
            return r.restriction.exact if r is not None else None
