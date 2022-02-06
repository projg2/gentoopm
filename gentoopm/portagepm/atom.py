#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections

import portage.exception as pe
from portage.dbapi.dep_expand import dep_expand
from portage.dep import match_from_list
from portage.versions import catsplit, pkgsplit, cpv_getversion, vercmp

from ..basepm.atom import PMAtom, PMPackageKey, PMPackageVersion, PMIncompletePackageKey
from ..exceptions import InvalidAtomStringError


class PortagePackageKey(PMPackageKey):
    @property
    def category(self):
        return catsplit(self)[0]

    @property
    def package(self):
        return catsplit(self)[1]


class PortageIncompletePackageKey(PMIncompletePackageKey, PortagePackageKey):
    def __new__(self, key):
        return PMIncompletePackageKey.__new__(self, catsplit(key)[1])


class PortagePackageVersion(PMPackageVersion):
    def __new__(self, cpv):
        return PMPackageVersion.__new__(self, cpv_getversion(cpv))

    def __init__(self, cpv):
        self._cpv = cpv

    @property
    def without_revision(self):
        return pkgsplit(self._cpv)[1]

    @property
    def revision(self):
        rs = pkgsplit(self._cpv)[2]
        assert rs.startswith("r")
        return int(rs[1:])

    def __lt__(self, other):
        return vercmp(str(self), str(other)) < 0


class FakeSettings(object):
    """
    Fake settings object, to satisfy cpv_expand().
    """

    def __getattr__(self, key):
        return lambda: collections.defaultdict(lambda: "")


def _get_atom(s):
    try:
        return dep_expand(s, settings=FakeSettings())
    except pe.InvalidAtom:
        raise InvalidAtomStringError("Incorrect atom: %s" % s)


class PortageAtom(object):
    def __new__(self, s):
        a = _get_atom(s)
        if catsplit(a.cp)[0] == "null":
            return UnexpandedPortageAtom(a)
        else:
            return CompletePortageAtom(a)


class CompletePortageAtom(PMAtom):
    def __init__(self, a):
        self._atom = a

    def _match(self, pkg):
        # SLOT matching requires metadata so delay it.
        if not match_from_list(self._atom, [pkg._cpv]):
            return False
        return not self._atom.slot or self._atom.slot == pkg.slot

    def __contains__(self, pkg):
        return self._match(pkg) != self.blocking

    def __str__(self):
        return str(self._atom)

    @property
    def complete(self):
        return True

    @property
    def blocking(self):
        return bool(self._atom.blocker)

    @property
    def key(self):
        return PortagePackageKey(self._atom.cp)

    @property
    def version(self):
        if self._atom.cp == self._atom.cpv:
            return None
        else:
            return PortagePackageVersion(self._atom.cpv)

    @property
    def slot(self):
        return self._atom.slot

    @property
    def subslot(self):
        return self._atom.sub_slot

    @property
    def slot_operator(self):
        return self._atom.slot_operator

    @property
    def repository(self):
        return self._atom.repo


class UncategorisedPackageWrapper(object):
    def __init__(self, pkg):
        self._pkg = pkg

    @property
    def _cpv(self):
        cpv = self._pkg._cpv
        return "null/%s" % catsplit(cpv)[1]

    @property
    def slot(self):
        return self._pkg.slot

    @property
    def subslot(self):
        return self._pkg.sub_slot

    @property
    def slot_operator(self):
        return self._atom.slot_operator


class UnexpandedPortageAtom(CompletePortageAtom):
    """
    An atom without a category specified.
    """

    def __contains__(self, pkg):
        return CompletePortageAtom.__contains__(self, UncategorisedPackageWrapper(pkg))

    def __str__(self):
        raise ValueError("Unable to stringify incomplete atom")

    @property
    def complete(self):
        return False

    @property
    def key(self):
        return PortageIncompletePackageKey(self._atom.cp)
