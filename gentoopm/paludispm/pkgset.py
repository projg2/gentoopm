#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from gentoopm.exceptions import EmptyPackageSetError, AmbiguousPackageSetError
from gentoopm.paludispm.atom import PaludisAtom

class PaludisPackageSet(object):
	def __init__(self, env, issorted = False):
		self._env = env
		self._sorted = issorted

	def filter(self, *args, **kwargs):
		newargs = [(a if not isinstance(a, str)
			else PaludisAtom(a)) for a in args]

		return PaludisFilteredPackageSet(self, newargs, kwargs)

	@property
	def best(self):
		if self._sorted:
			it = iter(self)

			try:
				f = next(it)
			except StopIteration:
				raise EmptyPackageSetError('.best called on an empty set')
			for p in it:
				if p.key != f.key:
					raise AmbiguousPackageSetError('.best called on a set of differently-named packages')

			try:
				return p
			except NameError:
				return f
		else:
			return PMPackageSet.best.fget(self)

class PaludisFilteredPackageSet(PaludisPackageSet, PMFilteredPackageSet):
	def __init__(self, pset, args, kwargs):
		PaludisPackageSet.__init__(self, pset._env, pset._sorted)
		PMFilteredPackageSet.__init__(self, pset, args, kwargs)
