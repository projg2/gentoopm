#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.repo import PMRepository
from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage, PMPackageMetadata
from gentoopm.portagepm.pkg import PortageCategory, PortagePackage, PortageCPV
from gentoopm.util import IterDictWrapper

class PortageDBCategory(PortageCategory):
	def __iter__(self):
		for p in self._dbapi.cp_all():
			cat = portage.versions.catsplit(p)[0]
			if cat == self.key:
				yield PortageDBPackage(p, self, self._dbapi)

class PortageDBPackage(PortagePackage):
	def __iter__(self):
		for p in self._dbapi.cp_list(self._qpn):
			yield PortageDBCPV(p, self, self._dbapi)

class PortageDBCPV(PortageCPV):
	key_name = 'PVR'
	def __init__(self, cpv, parent, dbapi):
		version = portage.versions.cpv_getversion(cpv)
		PMPackage.__init__(self, version, parent)
		self._cpv = cpv
		self._dbapi = dbapi

	@property
	def metadata(self):
		return PortageDBMetadata(self._cpv, self._dbapi)

class PortageDBMetadata(PMPackageMetadata):
	def __init__(self, cpv, dbapi):
		self._cpv = cpv
		self._dbapi = dbapi

	def __getitem__(self, key):
		return self._dbapi.aux_get(self._cpv, [key])[0]
	
class PortDBRepository(PMRepository):
	def __init__(self, dbapi):
		self._dbapi = dbapi

	_category_class = PortageDBCategory
	def __iter__(self):
		for c in self._dbapi.categories:
			pc = self._category_class(c, self, self._dbapi)
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

class VDBRepository(PortDBRepository):
	pass
