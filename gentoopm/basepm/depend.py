#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PMBaseDep(ABCObject):
	"""
	Base class for a dependency list holder.
	"""

	@abstractmethod
	def __iter__(self):
		"""
		Iterate over dependency items.

		@rtype: iter(L{PMBaseDep},L{PMAtom})
		"""
		pass

	@abstractproperty
	def without_conditionals(self):
		"""
		Return the depspec with all conditionals resolved.

		@type: L{PMUncondAllOfDep}
		"""
		pass

class PMUncondBaseDep(PMBaseDep):
	def __init__(self, parent):
		self._parent = parent

	@property
	def without_conditionals(self):
		return self

	def _iter_deps(self, deps):
		for d in deps:
			if isinstance(d, PMConditionalDep):
				if d.enabled:
					for d in self._iter_deps(d):
						yield d
			elif isinstance(d, PMOneOfDep):
				yield PMUncondOneOfDep(d)
			else:
				yield d

	def __iter__(self):
		return self._iter_deps(self._parent)

class PMConditionalDep(PMBaseDep):
	"""
	A conditional dependency set (enabled by a condition of some kind).
	"""

	@property
	def without_conditionals(self):
		return PMUncondAllOfDep((self,))

	@abstractproperty
	def enabled(self):
		"""
		Whether the dependency set is enabled (the condition is met).

		@type: bool
		"""
		pass

class PMAllOfDep(PMBaseDep):
	"""
	An all-of dependency block (C{( ... ... )}).
	"""

	@property
	def without_conditionals(self):
		return PMUncondAllOfDep(self)

class PMUncondAllOfDep(PMAllOfDep, PMUncondBaseDep):
	pass

class PMOneOfDep(PMBaseDep):
	"""
	A one-of dependency set (C{|| ( ... )}).
	"""

	@property
	def without_conditionals(self):
		return PMUncondOneOfDep(self)

class PMUncondOneOfDep(PMOneOfDep, PMUncondBaseDep):
	pass

class PMPackageDepSet(PMBaseDep):
	"""
	A base class representing a depset of a single package.
	"""

	@property
	def without_conditionals(self):
		return PMUncondAllOfDep(self)
