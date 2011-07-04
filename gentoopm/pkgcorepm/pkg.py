#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.restrictions.packages import PackageRestriction, AndRestriction
from pkgcore.restrictions.values import StrExactMatch

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage
from gentoopm.util import IterDictWrapper

class PkgCoreCategory(PMKeyedPackageDict):
	key_name = 'CATEGORY'
	def __iter__(self):
		repo = self.parent
		for p in repo._repo.packages[self.key]:
			yield PkgCorePackage(p, self)

	@property
	def packages(self):
		"""
		A convenience wrapper for the package list.
		"""
		return IterDictWrapper(self)

class PkgCorePackage(PMKeyedPackageDict):
	key_name = 'PN'
	def __iter__(self):
		r = AndRestriction(
			PackageRestriction("category", StrExactMatch(self.parent.key)),
			PackageRestriction("package", StrExactMatch(self.key))
		)

		repo = self.parent.parent
		for p in repo._repo.itermatch(r):
			yield PkgCoreEbuild(p, self)

	@property
	def versions(self):
		"""
		A convenience wrapper for the version list.
		"""
		return IterDictWrapper(self)

class PkgCoreEbuild(PMPackage):
	key_name = 'PVR'
	def __init__(self, pkg, parent):
		self._pkg = pkg
		pvr = pkg.version
		if pkg.revision:
			pvr += '-r%d' % pkg.revision
		PMPackage.__init__(self, pvr, parent)
