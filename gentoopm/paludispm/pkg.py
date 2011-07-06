#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage
from gentoopm.util import IterDictWrapper

class PaludisCategory(PMKeyedPackageDict):
	_key_name = 'CATEGORY'
	def __init__(self, category, parent):
		PMKeyedPackageDict.__init__(self, str(category), parent)

	def __iter__(self):
		repo = self._parent
		for p in repo._repo.package_names(self._key, []):
			yield PaludisPackage(p, self)

	@property
	def packages(self):
		"""
		A convenience wrapper for the package list.
		"""
		return IterDictWrapper(self)

class PaludisPackage(PMKeyedPackageDict):
	_key_name = 'PN'
	def __init__(self, qpn, parent):
		PMKeyedPackageDict.__init__(self, str(qpn.package), parent)
		self._qpn = qpn

	def __iter__(self):
		repo = self._parent._parent
		for p in repo._repo.package_ids(self._qpn, []):
			yield PaludisID(p, self)

	@property
	def versions(self):
		"""
		A convenience wrapper for the version list.
		"""
		return IterDictWrapper(self)

class PaludisID(PMPackage):
	_key_name = 'PVR'
	def __init__(self, pkg, parent):
		self._pkg = pkg
		PMPackage.__init__(self, str(pkg.version), parent)

	@property
	def metadata(self):
		return PaludisMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.fs_location_key().parse_value()

	def __cmp__(self, other):
		if not isinstance(other, PaludisID):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if self._pkg.name != other._pkg.name:
			raise TypeError('Unable to compare IDs with different PNs')
		return self._pkg.version.__cmp__(other._pkg.version)

class PaludisMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	def __getitem__(self, key):
		m = self._pkg.find_metadata(key)
		if m is None:
			return ''
		m = m.parse_value()
		if isinstance(m, paludis.StringSetIterable) \
				or isinstance(m, paludis.KeywordNameIterable):
			return ' '.join([str(x) for x in m])
		elif isinstance(m, paludis.AllDepSpec):
			raise NotImplementedError('Parsing %s is not supported yet.' % key)
		else:
			return str(m)
