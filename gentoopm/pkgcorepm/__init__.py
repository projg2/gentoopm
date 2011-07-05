#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.config import load_config

from gentoopm.basepm import PackageManager
from gentoopm.pkgcorepm.repo import PkgCoreRepoDict, \
		PkgCoreInstalledRepo

class PkgCorePM(PackageManager):
	name = 'pkgcore'

	def reload_config(self):
		c = load_config()
		self._domain = c.get_default('domain')

	@property
	def repositories(self):
		return PkgCoreRepoDict(self._domain.named_repos['repo-stack'])

	@property
	def installed(self):
		return PkgCoreInstalledRepo(self._domain.named_repos['vdb'])
