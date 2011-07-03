#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage

from pkgcore.restrictions.packages import PackageRestriction, AndRestriction
from pkgcore.restrictions.values import StrExactMatch

class PkgCoreCategory(PMKeyedPackageDict):
	def __iter__(self):
		repo = self.parent
		for p in repo._repo.packages[self.key]:
			yield PkgCorePackage(p, self)

class PkgCorePackage(PMKeyedPackageDict):
	def __iter__(self):
		r = AndRestriction(
			PackageRestriction("category", StrExactMatch(self.parent.key)),
			PackageRestriction("package", StrExactMatch(self.key))
		)

		repo = self.parent.parent
		for p in repo._repo.itermatch(r):
			yield PkgCoreEbuild(p, self)

class PkgCoreEbuild(PMPackage):
	def __init__(self, pkg, parent):
		self._pkg = pkg
		pvr = pkg.version
		if pkg.revision:
			pvr += '-r%d' % pkg.revision
		PMPackage.__init__(self, pvr, parent)
