#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from portage.dep import paren_reduce, use_reduce

from gentoopm.basepm.depend import PMPackageDepSet, PMConditionalDep, \
	PMAnyOfDep, PMAllOfDep, PMBaseDep
from gentoopm.portagepm.atom import PortageAtom

class PortageBaseDep(PMBaseDep):
	def __init__(self, deps, puse):
		self._deps = deps
		self._puse = puse

	def __iter__(self):
		it = iter(self._deps)
		for d in it:
			if d == '||':
				yield PortageAnyOfDep(next(it), self._puse)
			elif d == '&&':
				yield PortageAllOfDep(next(it), self._puse)
			elif d.endswith('?'):
				yield PortageConditionalUseDep(next(it),
						self._puse, d.rstrip('?'))
			else:
				yield PortageAtom(d)

class PortageAnyOfDep(PMAnyOfDep, PortageBaseDep):
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
		self._depstr = s
		PortageBaseDep.__init__(self, None, puse)

	def __iter__(self):
		if self._deps is None:
			self._deps = paren_reduce(self._depstr)
		return PortageBaseDep.__iter__(self)

	@property
	def without_conditionals(self):
		return PortageUncondAllOfDep(
				use_reduce(self._depstr, self._puse))

class PortageUncondDep(PortageBaseDep):
	def __init__(self, deps):
		self._deps = deps

	@property
	def without_conditionals(self):
		return self

	def __iter__(self):
		it = iter(self._deps)
		for d in it:
			if d == '||':
				yield PortageUncondAnyOfDep(next(it))
			elif d == '&&':
				yield PortageUncondAllOfDep(next(it))
			else:
				yield PortageAtom(d)

class PortageUncondAnyOfDep(PMAnyOfDep, PortageUncondDep):
	pass

class PortageUncondAllOfDep(PMAllOfDep, PortageUncondDep):
	pass
