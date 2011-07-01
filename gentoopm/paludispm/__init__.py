#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm import PackageManager
from gentoopm.paludispm.repo import PaludisRepoDict
from gentoopm.paludispm.shell import CaveShell

class PaludisPM(PackageManager):
	name = 'paludis'

	def reload_config(self):
		self._shell = CaveShell()

	@property
	def repositories(self):
		return PaludisRepoDict(self._shell)
