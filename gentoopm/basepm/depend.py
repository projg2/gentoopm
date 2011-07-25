#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PMPackageDepSet(ABCObject):
	"""
	A base class representing a depset of a single package.
	"""

	def __iter__(self):
		raise NotImplementedError('Working with raw depsets is not supported')

	@abstractproperty
	def evaluated(self):
		"""
		Get the evaluated depset (i.e. with all conditionals and one-of sets
		collapsed).

		@type: L{PMPackageFinalDepSet}
		"""
		pass

class PMPackageFinalDepSet(ABCObject):
	"""
	A base class representing a collapsed depset.
	"""

	@abstractmethod
	def __iter__(self):
		"""
		Iterate over dependency atoms.

		@rtype: iter(L{PMAtom})
		"""
		pass
