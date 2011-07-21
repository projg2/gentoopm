#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage, PMPackageDescription, \
		PMInstalledPackage, PMInstallablePackage
from gentoopm.basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from gentoopm.pkgcorepm.atom import PkgCoreAtom
from gentoopm.util import SpaceSepTuple

class PkgCorePackageSet(PMPackageSet):
	def filter(self, *args, **kwargs):
		newargs = [(a if not isinstance(a, str)
			else PkgCoreAtom(a)) for a in args]

		return PkgCoreFilteredPackageSet(self, newargs, kwargs)

class PkgCoreFilteredPackageSet(PkgCorePackageSet, PMFilteredPackageSet):
	pass

class PkgCorePackageDescription(PMPackageDescription):
	def __init__(self, pkg):
		self._pkg = pkg

	@property
	def short(self):
		return self._pkg.description

	@property
	def long(self):
		if hasattr(self._pkg, 'longdescription'):
			return self._pkg.longdescription
		else: # vdb, for example
			return None

class PkgCorePackage(PMPackage, PkgCoreAtom):
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
	def description(self):
		return PkgCorePackageDescription(self._pkg)

	@property
	def homepages(self):
		return SpaceSepTuple(self._pkg.homepage)

	@property
	def slotted(self):
		return PkgCoreAtom(self._pkg.slotted_atom)

	@property
	def unversioned(self):
		return PkgCoreAtom(self._pkg.unversioned_atom)

	@property
	def _r(self):
		return self._pkg

	@property
	def repository(self):
		return self._pkg.repo.repo_id

	def __str__(self):
		if self._repo_index != 0:
			s = '%s::%s' % (self._pkg.cpvstr, self._pkg.repo.repo_id)
		else:
			s = self._pkg.cpvstr
		return '=%s' % s

class PkgCoreInstallablePackage(PkgCorePackage, PMInstallablePackage):
	@property
	def inherits(self):
		try:
			l = self._pkg.data['_eclasses_']
		except KeyError:
			l = ()

		return SpaceSepTuple(l)

	def __lt__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					(self, other))
		return self._pkg < other._pkg \
				or other._repo_index < self._repo_index

class PkgCoreInstalledPackage(PkgCorePackage, PMInstalledPackage):
	@property
	def inherits(self):
		try:
			l = self._pkg.data['INHERITED']
		except KeyError:
			l = ()

		return SpaceSepTuple(l)

	def __lt__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					(self, other))
		return self._pkg < other._pkg

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
