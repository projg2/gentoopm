#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage

class PaludisID(PMPackage):
	def __init__(self, pkg, num = 0, enum_id = None):
		self._pkg = pkg
		self._num = num
		self._enum_id = enum_id

	@property
	def metadata(self):
		return PaludisMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.fs_location_key().parse_value()

	@property
	def id(self):
		return str(self._pkg)

	def __cmp__(self, other):
		if not isinstance(other, PaludisID):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if self._enum_id != other._enum_id:
			raise TypeError('Unable to compare results of two enumerations')
		return cmp(self._num, other._num)

class PaludisMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError('Unsupported metadata key: %s' % key)
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

	@property
	def CATEGORY(self):
		return str(self._pkg.name.category)

	@property
	def PN(self):
		return str(self._pkg.name.package)

	@property
	def PV(self):
		return str(self._pkg.version.remove_revision())

	@property
	def PR(self):
		return str(self._pkg.version.revision_only())

	@property
	def PVR(self):
		return str(self._pkg.version)
