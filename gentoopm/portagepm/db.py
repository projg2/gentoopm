#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.repo import PMRepository
from gentoopm.portagepm.pkg import PortageCPV

# XXX: cleanup all this mess!

class PortageDBCPV(PortageCPV):
	def __init__(self, cpv, dbapi):
		self._cpv = cpv
		self._dbapi = dbapi

	@property
	def metadata(self):
		return PortageDBMetadata(self._cpv, self._dbapi)

	@property
	def path(self):
		# .findname() gives .ebuild path
		return self._dbapi.getpath(self._cpv)

class PortageDBMetadata(PMPackageMetadata):
	def __init__(self, cpv, dbapi):
		self._cpv = cpv
		self._dbapi = dbapi

	def __getattr__(self, key):
		return self._dbapi.aux_get(self._cpv, [key])[0]

	@property
	def CATEGORY(self):
		return portage.versions.catsplit(self._cpv)[0]

	@property
	def PN(self):
		return portage.versions.catpkgsplit(self._cpv)[1]

	@property
	def PV(self):
		return portage.versions.pkgsplit(self._cpv)[1]

	@property
	def PR(self):
		return portage.versions.pkgsplit(self._cpv)[2]

	@property
	def PVR(self):
		return portage.versions.cpv_getversion(self._cpv)

class PortDBRepository(PMRepository):
	def __init__(self, dbapi):
		self._dbapi = dbapi

	def __iter__(self):
		for p in self._dbapi.cpv_all(): # XXX
			yield PortageDBCPV(p, self._dbapi)

class VDBRepository(PortDBRepository):
	pass
