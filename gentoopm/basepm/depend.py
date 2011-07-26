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

class PMConditionalDep(PMBaseDep):
	"""
	A conditional dependency set (enabled by a condition of some kind).
	"""

	@abstractproperty
	def enabled(self):
		"""
		Whether the dependency set is enabled (the condition is met).

		@type: bool
		"""
		pass

class PMOneOfDep(PMBaseDep):
	pass

class PMPackageDepSet(PMBaseDep):
	"""
	A base class representing a depset of a single package.
	"""
	pass
