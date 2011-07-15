#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.pkgset import PMPackageSet, PMFilteredPackageSet
from gentoopm.exceptions import EmptyPackageSetError, AmbiguousPackageSetError

class PaludisPackageSet(PMPackageSet):
	_sorted = False

	def filter(self, *args, **kwargs):
		return PaludisFilteredPackageSet(self, args, kwargs)

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

class PaludisFilteredPackageSet(PMFilteredPackageSet, PaludisPackageSet):
	def __init__(self, pset, args, kwargs):
		self._sorted = pset._sorted
		PMFilteredPackageSet.__init__(self, pset, args, kwargs)
