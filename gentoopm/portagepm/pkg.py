#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage

# XXX: cleanup all this mess!

class PortageCPV(PMPackage):
	def __init__(self, cpv, dbapi, tree):
		self._cpv = cpv
		self._dbapi = dbapi
		self._tree = tree

	@property
	def metadata(self):
		return PortageMetadata(self._cpv, self._dbapi, self._tree)

	@property
	def path(self):
		return self._dbapi.findname(self._cpv, self._tree)

	def __cmp__(self, other):
		if not isinstance(other, PortageCPV):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if portage.versions.cpv_getkey(self._cpv) != \
				portage.versions.cpv_getkey(other._cpv):
			raise TypeError('Unable to compare CPVs with different PNs')
		return portage.versions.vercmp(
				portage.versions.cpv_getversion(self._cpv),
				portage.versions.cpv_getversion(other._cpv))

class PortageMetadata(PMPackageMetadata):
	def __init__(self, cpv, dbapi, tree):
		self._cpv = cpv
		self._dbapi = dbapi
		self._tree = tree

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError('Unsupported metadata key: %s' % key)
		return self._dbapi.aux_get(self._cpv, [key],
				mytree = self._tree)[0]

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
