#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import functools, paludis

try:
	paludis.PackageDepSpec.slot_requirement
except (NameError, AttributeError):
	raise ImportError('paludis version too old (at least 0.64.2 required)')

from ..basepm import PackageManager

from .atom import PaludisAtom
from .config import PaludisConfig
from .repo import PaludisRepoDict, PaludisInstalledRepo, PaludisStackRepo

class PaludisPM(PackageManager):
	name = 'paludis'

	@property
	def version(self):
		return paludis.VERSION

	def reload_config(self):
		self._env = paludis.EnvironmentFactory.instance.create('')

	@property
	def repositories(self):
		return PaludisRepoDict(self._env)

	@property
	def root(self):
		return '/'

	@property
	def installed(self):
		return PaludisInstalledRepo(self._env, self.root)

	@property
	def stack(self):
		return PaludisStackRepo(self._env)

	@property
	def Atom(self):
		return functools.partial(PaludisAtom, env = self._env)

	@property
	def config(self):
		return PaludisConfig(self._env)
