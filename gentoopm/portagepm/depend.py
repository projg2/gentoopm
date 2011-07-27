#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from portage.dep import paren_reduce

from gentoopm.basepm.depend import PMPackageDepSet, PMConditionalDep, \
	PMOneOfDep, PMAllOfDep, PMBaseDep
from gentoopm.portagepm.atom import PortageAtom

class PortageBaseDep(PMBaseDep):
	def __init__(self, deps, puse):
		self._deps = deps
		self._puse = puse

	def __iter__(self):
		it = iter(self._deps)
		for d in it:
			if d == '||':
				yield PortageOneOfDep(next(it), self._puse)
			elif d == '&&':
				yield PortageAllOfDep(next(it), self._puse)
			elif d.endswith('?'):
				yield PortageConditionalUseDep(next(it),
						self._puse, d.rstrip('?'))
			else:
				yield PortageAtom(d)

class PortageOneOfDep(PMOneOfDep, PortageBaseDep):
	pass

class PortageAllOfDep(PMAllOfDep, PortageBaseDep):
	pass

class PortageConditionalUseDep(PMConditionalDep, PortageBaseDep):
	def __init__(self, deps, puse, flag):
		PortageBaseDep.__init__(self, deps, puse)
		self._flag = flag

	@property
	def enabled(self):
		return self._flag in self._puse

class PortagePackageDepSet(PMPackageDepSet, PortageBaseDep):
	def __init__(self, s, puse):
		PortageBaseDep.__init__(self, paren_reduce(s), puse)
