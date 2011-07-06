#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage

class PkgCorePackage(PMPackage):
	def __init__(self, pkg):
		self._pkg = pkg

	@property
	def metadata(self):
		return PkgCoreMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.path

	def __cmp__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if self._pkg.key != other._pkg.key:
			raise TypeError('Unable to compare ebuilds with different PNs')
		return self._pkg.__cmp__(other._pkg)

class PkgCoreMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	@property
	def EAPI(self):
		return self._pkg.eapi

	@property
	def INHERITED(self):
		return ' '.join(self._pkg.data['_eclasses_'].keys())

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError('Unsupported metadata key: %s' % key)
		try:
			return self._pkg.data[key]
		except KeyError:
			return ''

	@property
	def CATEGORY(self):
		return self._pkg.category

	@property
	def PN(self):
		return self._pkg.PN

	@property
	def PV(self):
		return self._pkg.version

	@property
	def PR(self):
		return 'r%d' % self._pkg.PR

	@property
	def P(self):
		return self._pkg.P

	@property
	def PVR(self):
		return self._pkg.fullver

	@property
	def PF(self):
		return self._pkg.PF
