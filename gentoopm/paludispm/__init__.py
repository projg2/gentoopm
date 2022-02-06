#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2017 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import functools, paludis

try:
    paludis.SlotExactFullRequirement.slots
except (NameError, AttributeError):
    raise ImportError(
        "paludis version too old (at least git d15113c5058/3.0.0 required)"
    )

from ..basepm import PackageManager

from .atom import PaludisAtom
from .config import PaludisConfig
from .repo import PaludisRepoDict, PaludisInstalledRepo, PaludisStackRepo


class PaludisPM(PackageManager):
    name = "paludis"

    @property
    def version(self):
        return paludis.VERSION

    def reload_config(self):
        config = "portage:%s" % self.config_root
        self._env = paludis.EnvironmentFactory.instance.create(config)

    @property
    def repositories(self):
        return PaludisRepoDict(self._env)

    @property
    def root(self):
        # FIXME
        return "/"

    @property
    def installed(self):
        return PaludisInstalledRepo(self._env, self.config_root)

    @property
    def stack(self):
        return PaludisStackRepo(self._env)

    @property
    def Atom(self):
        return functools.partial(PaludisAtom, env=self._env)

    @property
    def config(self):
        return PaludisConfig(self._env)
