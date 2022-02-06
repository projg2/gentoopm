#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os
from portage import create_trees, VERSION

from ..basepm import PackageManager

from .atom import PortageAtom
from .config import PortageConfig
from .repo import PortageRepoDict, VDBRepository


class PortagePM(PackageManager):
    name = "portage"

    @property
    def version(self):
        return VERSION

    def reload_config(self):
        kwargs = {}
        if self.config_root:
            kwargs["config_root"] = self.config_root
        trees = create_trees(**kwargs)
        tree = trees[max(trees)]
        self._root = max(trees)
        self._vardb = tree["vartree"].dbapi
        self._portdb = tree["porttree"].dbapi

    @property
    def repositories(self):
        return PortageRepoDict(self._portdb)

    @property
    def root(self):
        return self._root

    @property
    def installed(self):
        return VDBRepository(self._vardb)

    @property
    def Atom(self):
        return PortageAtom

    @property
    def config(self):
        return PortageConfig(self._portdb.settings)
