#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.versions

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage, PMPackageMetadata
from gentoopm.util import IterDictWrapper

class PortageCategory(PMKeyedPackageDict):
	_key_name = 'CATEGORY'
	def __init__(self, category, parent, dbapi):
		PMKeyedPackageDict.__init__(self, category, parent)
		self._dbapi = dbapi

	def __iter__(self):
		repo = self._parent.path

		for p in self._dbapi.cp_all(categories=(self._key,), trees=(repo,)):
			yield PortagePackage(p, self, self._dbapi)

	@property
	def packages(self):
		"""
		A convenience wrapper for the package list.
		"""
		return IterDictWrapper(self)

class PortagePackage(PMKeyedPackageDict):
	_key_name = 'PN'
	def __init__(self, qpn, parent, dbapi):
		pn = portage.versions.catsplit(qpn)[1]
		PMKeyedPackageDict.__init__(self, pn, parent)
		self._qpn = qpn
		self._dbapi = dbapi

	def __iter__(self):
		repo = self._parent._parent.path

		for p in self._dbapi.cp_list(self._qpn, mytree=repo):
			yield PortageCPV(p, self, self._dbapi)

	@property
	def versions(self):
		"""
		A convenience wrapper for the version list.
		"""
		return IterDictWrapper(self)

class PortageCPV(PMPackage):
	_key_name = 'PVR'
	def __init__(self, cpv, parent, dbapi):
		version = portage.versions.cpv_getversion(cpv)
		PMPackage.__init__(self, version, parent)
		self._cpv = cpv
		self._dbapi = dbapi

	@property
	def _repo_path(self):
		return self._parent._parent._parent.path

	@property
	def metadata(self):
		return PortageMetadata(self._cpv, self._dbapi, self._repo_path)

	@property
	def path(self):
		return self._dbapi.findname(self._cpv, self._repo_path)

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

	def __getitem__(self, key):
		return self._dbapi.aux_get(self._cpv, [key],
				mytree = self._tree)[0]
