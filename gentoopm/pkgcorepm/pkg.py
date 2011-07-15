#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage
from gentoopm.basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from gentoopm.pkgcorepm.atom import PkgCoreAtom

class PkgCorePackageSet(PMPackageSet):
	def filter(self, *args, **kwargs):
		newargs = [(a if not isinstance(a, str)
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
		return PkgCoreAtom('=%s' % self.id, self)

	def __lt__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					(self, other))
		return self._pkg < other._pkg \
				or other._repo_index < self._repo_index

class PkgCoreMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	@property
	def INHERITED(self):
		# vdb uses INHERITED
		# ebuilds use _eclasses_
		try:
			return self._pkg.data['INHERITED']
		except KeyError:
			pass
		try:
			return ' '.join(self._pkg.data['_eclasses_'].keys())
		except KeyError:
			return ''

	@property
	def DEPEND(self):
		return str(self._pkg.depends)

	@property
	def RDEPEND(self):
		return str(self._pkg.rdepends)

	@property
	def PDEPEND(self):
		return str(self._pkg.post_rdepends)

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError('Unsupported metadata key: %s' % key)
		v = getattr(self._pkg, key.lower())
		if isinstance(v, tuple) or isinstance(v, frozenset):
			return ' '.join(v)
		else:
			return str(v)
