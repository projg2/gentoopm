#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage, PMPackageMetadata
from gentoopm.util import IterDictWrapper

class PortageCategory(PMKeyedPackageDict):
	key_name = 'CATEGORY'
	def __init__(self, category, parent, dbapi):
		PMKeyedPackageDict.__init__(self, category, parent)
		self._dbapi = dbapi

	def __iter__(self):
		repo = self.parent.path

		for p in self._dbapi.cp_all(categories=(self.key,), trees=(repo,)):
			yield PortagePackage(p, self, self._dbapi)

	@property
	def packages(self):
		"""
		A convenience wrapper for the package list.
		"""
		return IterDictWrapper(self)

class PortagePackage(PMKeyedPackageDict):
	key_name = 'PN'
	def __init__(self, qpn, parent, dbapi):
		pn = portage.versions.catsplit(qpn)[1]
		PMKeyedPackageDict.__init__(self, pn, parent)
		self._qpn = qpn
		self._dbapi = dbapi

	def __iter__(self):
		repo = self.parent.parent.path

		for p in self._dbapi.cp_list(self._qpn, mytree=repo):
			yield PortageCPV(p, self, self._dbapi)

	@property
	def versions(self):
		"""
		A convenience wrapper for the version list.
		"""
		return IterDictWrapper(self)

class PortageCPV(PMPackage):
	key_name = 'PVR'
	def __init__(self, cpv, parent, dbapi):
		version = portage.versions.cpv_getversion(cpv)
		PMPackage.__init__(self, version, parent)
		self._cpv = cpv
		self._dbapi = dbapi

	@property
	def metadata(self):
		return PortageMetadata(self._cpv, self._dbapi)

class PortageMetadata(PMPackageMetadata):
	def __init__(self, cpv, dbapi):
		self._cpv = cpv
		self._dbapi = dbapi

	def __getitem__(self, key):
		return self._dbapi.aux_get(self._cpv, [key])[0]
