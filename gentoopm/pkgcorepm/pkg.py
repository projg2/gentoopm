#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage, PMPackageSet, PMFilteredPackageSet
from gentoopm.pkgcorepm.atom import PkgCoreAtom

class PkgCorePackageSet(PMPackageSet):
	def filter(self, *args, **kwargs):
		newargs = [(a if not isinstance(a, basestring)
			else PkgCoreAtom(a)) for a in args]

		return PkgCoreFilteredPackageSet(self, newargs, kwargs)

class PkgCoreFilteredPackageSet(PkgCorePackageSet, PMFilteredPackageSet):
	pass

class PkgCorePackage(PMPackage):
	def __init__(self, pkg, repo_index = 0):
		self._pkg = pkg
		self._repo_index = repo_index

	@property
	def metadata(self):
		return PkgCoreMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.path

	@property
	def key(self):
		return self._pkg.key

	@property
	def id(self):
		if self._repo_index != 0:
			return '%s::%s' % (self._pkg.cpvstr, self._pkg.repo.repo_id)
		else:
			return self._pkg.cpvstr

	@property
	def atom(self):
		return PkgCoreAtom('=%s' % self.id)

	def __cmp__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					(self, other))
		return cmp(self._pkg, other._pkg) \
				or cmp(other._repo_index, self._repo_index)

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
