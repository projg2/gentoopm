#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.ebuild.atom import atom
from pkgcore.restrictions.boolean import OrRestriction

from gentoopm.basepm.depend import PMPackageDepSet, PMPackageFinalDepSet
from gentoopm.pkgcorepm.atom import PkgCoreAtom

class PkgCorePackageDepSet(PMPackageDepSet):
	def __init__(self, deps, pkg):
		self._deps = deps
		self._pkg = pkg

	@property
	def evaluated(self):
		return PkgCorePackageFinalDepSet(
				self._deps.evaluate_depset(self._pkg.use))

class PkgCorePackageFinalDepSet(PMPackageFinalDepSet):
	def __init__(self, deps):
		self._deps = deps

	def _iter_deps(self, deps):
		for d in deps:
			if isinstance(d, atom):
				yield d
			elif isinstance(d, OrRestriction):
				for d in self._iter_deps((next(iter(d)),)): # XXX
					yield d
			else:
				raise NotImplementedError('Parsing %s not implemented' \
						% repr(d))

	def __iter__(self):
		for d in self._iter_deps(self._deps):
			yield PkgCoreAtom(d)
