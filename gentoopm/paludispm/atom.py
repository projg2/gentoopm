#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis, re

from ..basepm.atom import PMAtom, PMPackageKey, PMPackageVersion, PMIncompletePackageKey
from ..exceptions import InvalidAtomStringError

_category_wildcard_re = re.compile(r"\w")


class PaludisPackageKey(PMPackageKey):
    def __new__(self, key):
        return PMPackageKey.__new__(self, str(key))

    def __init__(self, key):
        self._k = key

    @property
    def category(self):
        return str(self._k.category)

    @property
    def package(self):
        return str(self._k.package)


class PaludisIncompletePackageKey(PMIncompletePackageKey):
    def __new__(self, key):
        return PMIncompletePackageKey.__new__(self, str(key))


class PaludisPackageVersion(PMPackageVersion):
    def __new__(self, ver):
        return PMPackageVersion.__new__(self, str(ver))

    def __init__(self, ver):
        self._v = ver

    @property
    def without_revision(self):
        return str(self._v.remove_revision())

    @property
    def revision(self):
        rs = self._v.revision_only()
        assert rs.startswith("r")
        return int(rs[1:])

    def __lt__(self, other):
        return self._v < other._v


class PaludisAtom(PMAtom):
    def _init_atom(self, s, env, wildcards=False):
        opts = (
            paludis.UserPackageDepSpecOptions()
            + paludis.UserPackageDepSpecOption.NO_DISAMBIGUATION
        )
        if wildcards:
            opts += paludis.UserPackageDepSpecOption.ALLOW_WILDCARDS

        try:
            self._atom = paludis.parse_user_package_dep_spec(
                s, env, opts, paludis.Filter.All()
            )
        except (
            paludis.BadVersionOperatorError,
            paludis.PackageDepSpecError,
            paludis.RepositoryNameError,
        ):
            raise InvalidAtomStringError("Incorrect atom: %s" % s)

    def __init__(self, s, env, block=""):
        self._incomplete = False
        self._blocking = block
        if isinstance(s, paludis.PackageDepSpec):
            self._atom = s
        else:
            try:
                self._init_atom(s, env)
            except InvalidAtomStringError:
                # try */ for the category
                self._init_atom(_category_wildcard_re.sub(r"*/\g<0>", s, 1), env, True)
                self._incomplete = True
        self._env = env

    def _match(self, pkg):
        # we have to implementing matching by hand, boo
        other = pkg.atom
        # 1) category, our may be unset
        if self.key.category is not None and self.key.category != other.key.category:
            return False
        # 2) package name
        if self.key.package != other.key.package:
            return False
        # 3) package version (if any requirement set)
        try:
            vr = next(iter(self._atom.version_requirements))
        except StopIteration:
            pass
        else:
            if not vr.version_operator.compare(pkg._pkg.version, vr.version_spec):
                return False
        # 4) slot
        if self.slot is not None and self.slot != other.slot:
            return False
        # 5) repository
        if self.repository is not None and self.repository != other.repository:
            return False
        return True

    def __contains__(self, pkg):
        return self._match(pkg) != self.blocking

    def __str__(self):
        if self._incomplete:
            raise ValueError("Unable to stringify incomplete atom")
        return "%s%s" % (self._blocking, str(self._atom))

    @property
    def complete(self):
        return not self._incomplete

    @property
    def blocking(self):
        return bool(self._blocking)

    @property
    def key(self):
        if self.complete:
            return PaludisPackageKey(self._atom.package)
        else:
            return PaludisIncompletePackageKey(self._atom.package_name_part)

    @property
    def version(self):
        try:
            vr = next(iter(self._atom.version_requirements))
        except StopIteration:
            return None
        return PaludisPackageVersion(vr.version_spec)

    @property
    def slot(self):
        sreq = self._atom.slot_requirement
        if sreq is None:
            return None
        if isinstance(sreq, paludis.SlotExactPartialRequirement):  # :x
            return str(sreq.slot)
        if isinstance(sreq, paludis.SlotExactFullRequirement):  # :x/y
            return str(sreq.slots[0])
        if isinstance(sreq, paludis.SlotAnyAtAllLockedRequirement):  # :=
            return None
        if isinstance(sreq, paludis.SlotAnyPartialLockedRequirement):  # :x=
            return None
        if isinstance(sreq, paludis.SlotAnyUnlockedRequirement):  # :*
            return None
        raise NotImplementedError("Unknown slot requirement type %s" % repr(sreq))

    @property
    def subslot(self):
        sreq = self._atom.slot_requirement
        if sreq is None:
            return None
        if isinstance(sreq, paludis.SlotExactPartialRequirement):  # :x
            return None
        if isinstance(sreq, paludis.SlotExactFullRequirement):  # :x/y
            return str(sreq.slots[1])
        if isinstance(sreq, paludis.SlotAnyAtAllLockedRequirement):  # :=
            return None
        if isinstance(sreq, paludis.SlotAnyPartialLockedRequirement):  # :x=
            return None
        if isinstance(sreq, paludis.SlotAnyUnlockedRequirement):  # :*
            return None
        raise NotImplementedError("Unknown slot requirement type %s" % repr(sreq))

    @property
    def slot_operator(self):
        sreq = self._atom.slot_requirement
        if sreq is None:
            return None
        if isinstance(sreq, paludis.SlotExactPartialRequirement):  # :x
            return None
        if isinstance(sreq, paludis.SlotExactFullRequirement):  # :x/y
            return None
        if isinstance(sreq, paludis.SlotAnyAtAllLockedRequirement):  # :=
            return "="
        if isinstance(sreq, paludis.SlotAnyPartialLockedRequirement):  # :x=
            return "="
        if isinstance(sreq, paludis.SlotAnyUnlockedRequirement):  # :*
            return "*"
        raise NotImplementedError("Unknown slot requirement type %s" % repr(sreq))

    @property
    def repository(self):
        if self._atom.in_repository is None:
            return None
        return str(self._atom.in_repository)
