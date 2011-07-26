#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.ebuild.atom import atom
from pkgcore.restrictions.boolean import OrRestriction
from pkgcore.restrictions.packages import Conditional

from gentoopm.basepm.depend import PMPackageDepSet, PMConditionalDep, \
	PMOneOfDep, PMBaseDep
from gentoopm.pkgcorepm.atom import PkgCoreAtom

class PkgCoreBaseDep(PMBaseDep):
	def __init__(self, deps, pkg):
		self._deps = deps
		self._pkg = pkg

	def __iter__(self):
		for d in self._deps:
			if isinstance(d, atom):
				yield PkgCoreAtom(d)
			elif isinstance(d, OrRestriction):
				yield PkgCoreOneOfDep(d, self._pkg)
			elif isinstance(d, Conditional) and d.attr == 'use':
				yield PkgCoreConditionalUseDep(d, self._pkg)
			else:
				raise NotImplementedError('Parsing %s not implemented' \
						% repr(d))

class PkgCoreOneOfDep(PMOneOfDep, PkgCoreBaseDep):
	pass

class PkgCoreConditionalUseDep(PMConditionalDep, PkgCoreBaseDep):
	@property
	def enabled(self):
		return self._deps.restriction.match(self._pkg.use)

class PkgCorePackageDepSet(PMPackageDepSet, PkgCoreBaseDep):
	@property
	def without_conditionals(self):
		return PkgCoreUncondPackageDepSet(
				self._deps.evaluate_depset(self._pkg.use))

class PkgCoreUncondDep(PkgCoreBaseDep):
	def __init__(self, deps):
		self._deps = deps

	@property
	def without_conditionals(self):
		return self

	def __iter__(self):
		for d in self._deps:
			if isinstance(d, atom):
				yield PkgCoreAtom(d)
			elif isinstance(d, OrRestriction):
				yield PkgCoreUncondOneOfDep(d)
			else:
				raise NotImplementedError('Parsing %s not implemented' \
						% repr(d))

class PkgCoreUncondOneOfDep(PMOneOfDep, PkgCoreUncondDep):
	pass

class PkgCoreUncondPackageDepSet(PkgCoreUncondDep):
	pass
