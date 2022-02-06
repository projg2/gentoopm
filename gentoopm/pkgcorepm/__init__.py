#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2017-2021 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from distutils.version import StrictVersion
import os
import os.path

from pkgcore import __version__ as pkgcore_version_raw
from pkgcore.config import load_config

from ..basepm import PackageManager

from .atom import PkgCoreAtom
from .config import PkgCoreConfig
from .repo import PkgCoreRepoDict, PkgCoreInstalledRepo


PKGCORE_VERSION = StrictVersion(pkgcore_version_raw)


class PkgCorePM(PackageManager):
    name = "pkgcore"

    @property
    def version(self):
        return pkgcore_version_raw

    def reload_config(self):
        config_root = os.environ.get("PORTAGE_CONFIGROOT")
        if self.config_root != "":
            config_root = self.config_root
        kwargs = {}
        if config_root != "":
            if PKGCORE_VERSION >= "0.11.7":
                kwargs["location"] = os.path.join(config_root, "etc", "portage")
            else:
                kwargs["configroot"] = config_root
        c = load_config(**kwargs)
        self._domain = c.get_default("domain")

    @property
    def repositories(self):
        return PkgCoreRepoDict(self._domain)

    @property
    def root(self):
        return self._domain.root

    @property
    def installed(self):
        repos = self._domain.repos_raw
        return PkgCoreInstalledRepo(repos["vdb"], self._domain)

    @property
    def Atom(self):
        return PkgCoreAtom

    @property
    def config(self):
        return PkgCoreConfig(self._domain)
