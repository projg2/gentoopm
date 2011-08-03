#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.pkg import PMPackage, PMPackageDescription, \
		PMInstalledPackage, PMInstallablePackage, PMBoundPackageKey, \
		PMPackageState, PMUseFlag
from gentoopm.basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from gentoopm.pkgcorepm.atom import PkgCoreAtom, PkgCorePackageKey
from gentoopm.pkgcorepm.contents import PkgCorePackageContents
from gentoopm.pkgcorepm.depend import PkgCorePackageDepSet
from gentoopm.util import SpaceSepTuple, SpaceSepFrozenSet

class PkgCorePackageSet(PMPackageSet):
	def filter(self, *args, **kwargs):
		newargs = [(a if not isinstance(a, str)
			else PkgCoreAtom(a)) for a in args]

		return PkgCoreFilteredPackageSet(self, newargs, kwargs)

class PkgCoreFilteredPackageSet(PkgCorePackageSet, PMFilteredPackageSet):
	pass

class PkgCoreBoundPackageKey(PkgCorePackageKey, PMBoundPackageKey):
	@property
	def state(self):
		return PMPackageState(
				installable = not self._atom.built,
				installed = self._atom.built)

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

class PkgCoreUseFlag(PMUseFlag):
	def __init__(self, s, enabled_use):
		PMUseFlag.__init__(self, s)
		self._enabled = self.name in enabled_use

	@property
	def enabled(self):
		return self._enabled

class PkgCoreUseSet(SpaceSepFrozenSet):
	def __new__(self, iuse, use):
		def _get_iuse():
			for u in iuse:
				yield PkgCoreUseFlag(u, use)

		self._use = use
		return SpaceSepFrozenSet.__new__(self, _get_iuse())

	def __getitem__(self, k):
		try:
			return SpaceSepFrozenSet.__getitem__(self, k)
		except KeyError:
			# XXX, incorrect flags?
			return PkgCoreUseFlag(k, self._use)

class PkgCorePackage(PMPackage, PkgCoreAtom):
	def __init__(self, pkg, repo_index = 0):
		self._pkg = pkg
		self._repo_index = repo_index

	@property
	def key(self):
		return PkgCoreBoundPackageKey(self._pkg)

	@property
	def path(self):
		return self._pkg.path

	@property
	def eapi(self):
		return str(self._pkg.eapi)

	@property
	def description(self):
		return PkgCorePackageDescription(self._pkg)

	@property
	def homepages(self):
		return SpaceSepTuple(self._pkg.homepage)

	@property
	def keywords(self):
		return SpaceSepFrozenSet(self._pkg.keywords)

	@property
	def defined_phases(self):
		return SpaceSepFrozenSet(self._pkg.defined_phases)

	@property
	def use(self):
		return PkgCoreUseSet(self._pkg.iuse, self._pkg.use)

	@property
	def slotted_atom(self):
		return PkgCoreAtom(self._pkg.slotted_atom)

	@property
	def unversioned_atom(self):
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

		return SpaceSepFrozenSet(l)

	@property
	def build_dependencies(self):
		return PkgCorePackageDepSet(self._pkg._raw_pkg.depends,
				self._pkg)

	@property
	def run_dependencies(self):
		return PkgCorePackageDepSet(self._pkg._raw_pkg.rdepends,
				self._pkg)

	@property
	def post_dependencies(self):
		return PkgCorePackageDepSet(self._pkg._raw_pkg.post_rdepends,
				self._pkg)

	@property
	def required_use(self):
		return PkgCorePackageDepSet(self._pkg._raw_pkg.required_use,
				self._pkg)

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

		return SpaceSepFrozenSet(l)

	@property
	def build_dependencies(self):
		return PkgCorePackageDepSet(self._pkg.depends,
				self._pkg)

	@property
	def run_dependencies(self):
		return PkgCorePackageDepSet(self._pkg.rdepends,
				self._pkg)

	@property
	def post_dependencies(self):
		return PkgCorePackageDepSet(self._pkg.pdepends,
				self._pkg)

	@property
	def required_use(self):
		return PkgCorePackageDepSet(self._pkg.required_use,
				self._pkg)

	@property
	def contents(self):
		return PkgCorePackageContents(self._pkg.contents)

	def __lt__(self, other):
		if not isinstance(other, PkgCorePackage):
			raise TypeError('Unable to compare %s against %s' % \
					(self, other))
		return self._pkg < other._pkg
