#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from portage.dep import paren_reduce

from gentoopm.basepm.depend import PMPackageDepSet, PMConditionalDep, \
	PMOneOfDep, PMAllOfDep, PMBaseDep
from gentoopm.portagepm.atom import PortageAtom

class PortageBaseDep(PMBaseDep):
	def __init__(self, deps):
		self._deps = deps

	def __iter__(self):
		it = iter(self._deps)
		for d in it:
			if d == '||':
				yield PortageOneOfDep(next(it))
			elif d == '&&':
				yield PortageAllOfDep(next(it))
			elif d.endswith('?'):
				yield PortageConditionalUseDep(next(it))
			else:
				yield PortageAtom(d)

class PortageOneOfDep(PMOneOfDep, PortageBaseDep):
	pass

class PortageAllOfDep(PMAllOfDep, PortageBaseDep):
	pass

class PortageConditionalUseDep(PMConditionalDep, PortageBaseDep):
	@property
	def enabled(self):
		# XXX
		raise NotImplementedError()

class PortagePackageDepSet(PMPackageDepSet, PortageBaseDep):
	def __init__(self, s):
		self._deps = paren_reduce(s)
