#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.repo import PMRepository
from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage, PMPackageMetadata
from gentoopm.portagepm.pkg import PortageCategory, PortagePackage, PortageCPV
from gentoopm.util import IterDictWrapper

class VDBRepository(PMRepository):
	def __init__(self, vardbapi):
		self._dbapi = vardbapi

	@property
	def name(self):
		return None

	@property
	def path(self):
		return None

	def __iter__(self):
		for c in self._dbapi.categories:
			pc = PortageVDBCategory(c, self, self._dbapi)
			try:
				next(iter(pc))
			except StopIteration: # omit empty categories
				pass
			else:
				yield pc

	@property
	def categories(self):
		"""
		A convenience wrapper for the category list.
		"""
		return IterDictWrapper(self)
	
class PortageVDBCategory(PortageCategory):
	def __iter__(self):
		for p in self._dbapi.cp_all():
			cat = portage.versions.catsplit(p)[0]
			if cat == self.key:
				yield PortageVDBPackage(p, self, self._dbapi)

class PortageVDBPackage(PortagePackage):
	def __iter__(self):
		for p in self._dbapi.cp_list(self._qpn):
			yield PortageVDBCPV(p, self, self._dbapi)

class PortageVDBCPV(PortageCPV):
	key_name = 'PVR'
	def __init__(self, cpv, parent, dbapi):
		version = portage.versions.cpv_getversion(cpv)
		PMPackage.__init__(self, version, parent)
		self._cpv = cpv
		self._dbapi = dbapi

	@property
	def metadata(self):
		return PortageVDBMetadata(self._cpv, self._dbapi)

class PortageVDBMetadata(PMPackageMetadata):
	def __init__(self, cpv, dbapi):
		self._cpv = cpv
		self._dbapi = dbapi

	def __getitem__(self, key):
		return self._dbapi.aux_get(self._cpv, [key])[0]
