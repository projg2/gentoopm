# (c) 2017-2024 Michał Górny <mgorny@gentoo.org>
# (c) 2024 Anna <cyber@sysrq.in>
# SPDX-License-Identifier: GPL-2.0-or-later

import errno
import typing
from collections.abc import Sequence
from pathlib import Path

from portage.versions import cpv_getkey
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
from ..basepm.upstream import (
    PMUpstream,
    PMUpstreamDoc,
    PMUpstreamMaintainer,
    PMUpstreamRemoteID,
)
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

    @property
    def license(self):
        return PortagePackageDepSet(
            self._aux_get("LICENSE"), self._applied_use, str
        )

    @property
    def properties(self):
        return PortagePackageDepSet(
            self._aux_get("PROPERTIES"), self._applied_use, str
        )

    @property
    def restrict(self):
        return PortagePackageDepSet(
            self._aux_get("RESTRICT"), self._applied_use, str
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


class PortageUpstreamDoc(PMUpstreamDoc):
    def __new__(cls, doc: Sequence[str]):
        return PMUpstreamDoc.__new__(cls, doc[0], doc[1] or "en")


class PortageUpstreamMaintainer(PMUpstreamMaintainer):
    def __new__(cls, m):
        return PMUpstreamMaintainer.__new__(cls, m.name, m.email, m.status)


class PortageUpstreamRemoteID(PMUpstreamRemoteID):
    def __new__(cls, remote_id: Sequence[str]):
        return PMUpstreamRemoteID.__new__(cls, remote_id[0], remote_id[1])


class PortageUpstream(PMUpstream):
    def __init__(self, meta: MetaDataXML):
        self._bugs_to: typing.Optional[str] = None
        self._changelog: typing.Optional[str] = None
        self._docs: list[PortageUpstreamDoc] = []
        self._maintainers: list[PortageUpstreamMaintainer] = []
        self._remote_ids: list[PortageUpstreamRemoteID] = []

        if meta is None:
            return

        upstreams = meta.upstream()
        if len(upstreams) == 0:
            return

        upstream = upstreams[-1]
        if len(upstream.bugtrackers) != 0:
            self._bugs_to = upstream.bugtrackers[-1]
        if len(upstream.changelogs) != 0:
            self._changelog = upstream.changelogs[-1]

        for doc in upstream.docs:
            self._docs.append(PortageUpstreamDoc(doc))

        for maintainer in filter(lambda m: m.name, upstream.maintainers):
            self._maintainers.append(PortageUpstreamMaintainer(maintainer))

        for remote_id in filter(all, upstream.remoteids):
            self._remote_ids.append(PortageUpstreamRemoteID(remote_id))

    @property
    def bugs_to(self) -> typing.Optional[str]:
        return self._bugs_to

    @property
    def changelog(self) -> typing.Optional[str]:
        return self._changelog

    @property
    def docs(self) -> Sequence[PortageUpstreamDoc]:
        return tuple(self._docs)

    @property
    def maintainers(self) -> Sequence[PortageUpstreamMaintainer]:
        return tuple(self._maintainers)

    @property
    def remote_ids(self) -> Sequence[PortageUpstreamRemoteID]:
        return tuple(self._remote_ids)


class PortageCPV(PortageDBCPV, PMInstallablePackage):
    def __init__(self, cpv, dbapi, tree, repo_prio):
        PortageDBCPV.__init__(self, cpv, dbapi)
        self._tree = tree
        self._repo_prio = repo_prio

    @property
    def _metadata(self) -> typing.Optional[MetaDataXML]:
        # yes, seriously, the only API portage has is direct parser
        # for the XML file
        xml_path = Path(self.path).parent / "metadata.xml"
        try:
            return MetaDataXML(xml_path, None)
        except (IOError, OSError) as e:
            if e.errno == errno.ENOENT:
                return None
            raise e

    @property
    def path(self):
        return self._dbapi.findname(self._cpv, self._tree)

    @property
    def repository(self):
        return self._dbapi.getRepositoryName(self._tree)

    @property
    def maintainers(self) -> Sequence[PortagePackageMaintainer]:
        if (meta := self._metadata) is None:
            return tuple()
        return tuple(PortagePackageMaintainer(m) for m in meta.maintainers())

    @property
    def upstream(self) -> PortageUpstream:
        return PortageUpstream(self._metadata)

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
