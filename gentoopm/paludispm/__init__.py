#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm import PackageManager
from gentoopm.paludispm.repo import PaludisRepoDict

class PaludisPM(PackageManager):
	name = 'paludis'

	def reload_config(self):
		self._env = paludis.EnvironmentFactory.instance.create('')

	@property
	def repositories(self):
		return PaludisRepoDict(self._env)
