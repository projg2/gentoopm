#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import functools, paludis

from gentoopm.basepm import PackageManager
from gentoopm.paludispm.atom import PaludisAtom
from gentoopm.paludispm.config import PaludisConfig
from gentoopm.paludispm.repo import PaludisRepoDict, PaludisInstalledRepo, \
		PaludisStackRepo

class PaludisPM(PackageManager):
	name = 'paludis'

	def reload_config(self):
		self._env = paludis.EnvironmentFactory.instance.create('')

	@property
	def repositories(self):
		return PaludisRepoDict(self._env)

	@property
	def installed(self):
		return PaludisInstalledRepo(self._env)

	@property
	def stack(self):
		return PaludisStackRepo(self._env)

	@property
	def Atom(self):
		return functools.partial(PaludisAtom, env = self._env)

	@property
	def config(self):
		return PaludisConfig(self._env)
