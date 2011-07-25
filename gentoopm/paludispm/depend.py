#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.depend import PMPackageDepSet, \
		PMPackageFinalDepSet
from gentoopm.paludispm.atom import PaludisAtom

class PaludisPackageDepSet(PMPackageDepSet):
	def __init__(self, deps, pkg):
		self._deps = deps
		self._pkg = pkg

	@property
	def evaluated(self):
		return PaludisPackageFinalDepSet(
				self._deps, self._pkg)

class PaludisPackageFinalDepSet(PMPackageFinalDepSet):
	def __init__(self, deps, pkg):
		self._deps = deps
		self._pkg = pkg

	def _ideps(self, deps):
		for d in deps:
			if isinstance(d, paludis.PackageDepSpec):
				yield PaludisAtom(d, self._pkg._env)
			elif isinstance(d, paludis.AnyDepSpec):
				# XXX, use something better here
				for a in self._ideps((next(iter(d)),)):
					yield a
			elif isinstance(d, paludis.ConditionalDepSpec):
				if d.condition_met(self._pkg._env, self._pkg._pkg):
					for a in self._ideps(d):
						yield a
			else:
				raise NotImplementedError('Unable to parse %s' % repr(d))

	def __iter__(self):
		for r in self._ideps(self._deps):
			yield r
