#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2017 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os

from pkgcore import __version__ as pkgcore_version
from pkgcore.config import load_config

from ..basepm import PackageManager

from .atom import PkgCoreAtom
from .config import PkgCoreConfig
from .repo import PkgCoreRepoDict, PkgCoreInstalledRepo

class PkgCorePM(PackageManager):
	name = 'pkgcore'

	@property
	def version(self):
		return pkgcore_version

	def reload_config(self):
		if (self.config_root != '' and (self.config_root !=
				os.environ.get('PORTAGE_CONFIGROOT', ''))):
			raise NotImplementedError('pkgcore supports only PORTAGE_CONFIGROOT')
		c = load_config()
		self._domain = c.get_default('domain')

	@property
	def repositories(self):
		return PkgCoreRepoDict(self._domain)

	@property
	def root(self):
		return self._domain.root

	@property
	def installed(self):
		repos = self._domain.repos_raw
		return PkgCoreInstalledRepo(repos['vdb'], self._domain)

	@property
	def Atom(self):
		return PkgCoreAtom

	@property
	def config(self):
		return PkgCoreConfig(self._domain)
