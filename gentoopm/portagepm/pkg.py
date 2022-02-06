#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2017 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import errno
import os.path

from portage.versions import cpv_getkey, cpv_getversion, vercmp
from portage.xml.metadata import MetaDataXML

from ..basepm.depend import PMRequiredUseAtom
from ..basepm.pkg import (
    PMPackage,
    PMPackageDescription,
    PMInstalledPackage,
    PMInstallablePackage,
    PMBoundPackageKey,
    PMPackageState,
    PMUseFlag,
    PMPackageMaintainer,
)
from ..basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from ..util import SpaceSepTuple, SpaceSepFrozenSet

from .atom import (
    PortageAtom,
    CompletePortageAtom,
    PortagePackageKey,
    PortagePackageVersion,
    _get_atom,
)
from .contents import PortagePackageContents
from .depend import PortagePackageDepSet


class PortagePackageSet(PMPackageSet):
    def filter(self, *args, **kwargs):
        newargs = [(a if not isinstance(a, str) else PortageAtom(a)) for a in args]

        return PortageFilteredPackageSet(self, newargs, kwargs)


class PortageFilteredPackageSet(PortagePackageSet, PMFilteredPackageSet):
    pass


class PortageBoundPackageKey(PortagePackageKey, PMBoundPackageKey):
    def __new__(self, cp, pkg):
        return PortagePackageKey.__new__(self, cp)

    def __init__(self, cp, pkg):
        self._state = PMPackageState(
            installable=isinstance(pkg, PortageCPV),
            installed=isinstance(pkg, PortageVDBCPV),
        )

    @property
    def state(self):
        return self._state


class PortagePackageDescription(PMPackageDescription):
    def __init__(self, pkg):
        self._pkg = pkg

    @property
    def short(self):
        return self._pkg._aux_get("DESCRIPTION")

    @property
    def long(self):
        """
        The long package description.

        @type: string/C{None}
        @bug: Portage doesn't support parsing metadata.xml.
        """
        return None  # XXX


class PortageUseFlag(PMUseFlag):
    def __new__(self, s, enabled_use):
        return PMUseFlag.__new__(self, s)

    def __init__(self, s, enabled_use):
        self._enabled = self.name in enabled_use

    @property
    def enabled(self):
        return self._enabled


class PortageUseSet(SpaceSepFrozenSet):
    def __new__(self, iuse, use):
        def _get_iuse():
            for u in iuse:
                yield PortageUseFlag(u, use)

        self._use = use
        return SpaceSepFrozenSet.__new__(self, _get_iuse())

    def __getitem__(self, k):
        try:
            return SpaceSepFrozenSet.__getitem__(self, k)
        except KeyError:
            # XXX, incorrect flags?
            return PortageUseFlag(k, self._use)


class PortagePackageMaintainer(PMPackageMaintainer):
    def __new__(self, m):
        ret = PMPackageMaintainer.__new__(self, m.email, m.name)
        ret._m = m
        return ret

    @property
    def description(self):
        return self._m.description


class PortageDBCPV(PMPackage, CompletePortageAtom):
    def __init__(self, cpv, dbapi):
        self._cpv = cpv
        self._dbapi = dbapi

    @property
    def path(self):
        # .findname() gives .ebuild path
        return self._dbapi.getpath(self._cpv)

    @property
    def key(self):
        return PortageBoundPackageKey(cpv_getkey(self._cpv), self)

    @property
    def version(self):
        return PortagePackageVersion(self._cpv)

    def _aux_get(self, *keys):
        val = map(str, self._dbapi.aux_get(self._cpv, keys))
        if len(keys) == 1:
            return next(iter(val))
        else:
            return tuple(val)

    @property
    def eapi(self):
        return self._aux_get("EAPI")

    @property
    def description(self):
        return PortagePackageDescription(self)

    @property
    def inherits(self):
        return SpaceSepFrozenSet(self._aux_get("INHERITED"))

    @property
    def defined_phases(self):
        v = self._aux_get("DEFINED_PHASES")
        if v == "-":
            return SpaceSepFrozenSet(())
        return SpaceSepFrozenSet(v)

    @property
    def homepages(self):
        return SpaceSepTuple(self._aux_get("HOMEPAGE"))

    @property
    def keywords(self):
        return SpaceSepFrozenSet(self._aux_get("KEYWORDS"))

    @property
    def slot(self):
        return self._aux_get("SLOT").split("/")[0]

    @property
    def subslot(self):
        split_slot = self._aux_get("SLOT").split("/")
        assert len(split_slot) <= 2
        # subslot defaults to slot if not explicitly provided
        return split_slot[-1]

    @property
    def repository(self):
        raise None

    @property
    def use(self):
        return PortageUseSet(self._aux_get("IUSE").split(), self._applied_use)

    @property
    def slotted_atom(self):
        cp = str(self.key)
        slot = self.slot
        return PortageAtom("%s:%s" % (cp, slot))

    @property
    def unversioned_atom(self):
        return PortageAtom(str(self.key))

    @property
    def _atom(self):
        return _get_atom(str(self))

    @property
    def _applied_use(self):
        class LazyUseGetter(object):
            def __init__(self, dbapi, cpv):
                self._cpv = cpv
                self._dbapi = dbapi
                self._settings = dbapi.settings
                self._use_cache = None

            @property
            def _use_set(self):
                if self._use_cache is None:
                    s = self._settings.__class__(clone=self._settings)
                    # XXX: repos? _emerge.Package or compatible API?
                    s.setcpv(self._cpv, mydb=self._dbapi)
                    self._use_cache = frozenset(s["PORTAGE_USE"].split())
                return self._use_cache

            def __iter__(self):
                return iter(self._use_set)

            def __contains__(self, k):
                return k in self._use_set

        return LazyUseGetter(self._dbapi, self._cpv)

    @property
    def build_dependencies(self):
        return PortagePackageDepSet(
            self._aux_get("DEPEND"), self._applied_use, PortageAtom
        )

    @property
    def cbuild_build_dependencies(self):
        if self.eapi in (str(x) for x in range(0, 7)):
            return self.build_dependencies
        return PortagePackageDepSet(
            self._aux_get("BDEPEND"), self._applied_use, PortageAtom
        )

    @property
    def run_dependencies(self):
        return PortagePackageDepSet(
            self._aux_get("RDEPEND"), self._applied_use, PortageAtom
        )

    @property
    def post_dependencies(self):
        return PortagePackageDepSet(
            self._aux_get("PDEPEND"), self._applied_use, PortageAtom
        )

    @property
    def required_use(self):
        return PortagePackageDepSet(
            self._aux_get("REQUIRED_USE"), self._applied_use, PMRequiredUseAtom
        )

    def __str__(self):
        return "=%s" % self._cpv

    def __lt__(self, other):
        if not isinstance(other, PortageDBCPV):
            raise TypeError("Unable to compare %s against %s" % (self, other))

        if self.key < other.key:
            return True
        if self.key == other.key:
            return self.version < other.version
        return False


class PortageCPV(PortageDBCPV, PMInstallablePackage):
    def __init__(self, cpv, dbapi, tree, repo_prio):
        PortageDBCPV.__init__(self, cpv, dbapi)
        self._tree = tree
        self._repo_prio = repo_prio

    @property
    def path(self):
        return self._dbapi.findname(self._cpv, self._tree)

    @property
    def repository(self):
        return self._dbapi.getRepositoryName(self._tree)

    @property
    def maintainers(self):
        # yes, seriously, the only API portage has is direct parser
        # for the XML file
        xml_path = os.path.join(os.path.dirname(self.path), "metadata.xml")
        try:
            meta = MetaDataXML(xml_path, None)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                return ()
            raise

        return tuple(PortagePackageMaintainer(m) for m in meta.maintainers())

    @property
    def repo_masked(self):
        raise NotImplementedError(".repo_masked is not implemented for Portage")

    def _aux_get(self, *keys):
        val = map(str, self._dbapi.aux_get(self._cpv, keys, mytree=self._tree))
        if len(keys) == 1:
            return next(iter(val))
        else:
            return tuple(val)

    def __str__(self):
        return "=%s::%s" % (self._cpv, self.repository)

    def __lt__(self, other):
        if not isinstance(other, PortageCPV):
            raise TypeError("Unable to compare %s against %s" % (self, other))

        if self.key < other.key:
            return True
        if self.key == other.key:
            if self.version < other.version:
                return True
            if self.version == other.version:
                return self._repo_prio < other._repo_prio
        return False


class PortageVDBCPV(PortageDBCPV, PMInstalledPackage):
    @property
    def contents(self):
        return PortagePackageContents(self._dbapi._dblink(self._cpv))
