#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod

from gentoopm.util import ABCObject

class PMPackageMatcher(ABCObject):
	"""
	Base class for a package matcher.

	Package matcher is basically a function (or function class wrapper) which
	checks the package for match.
	"""

	@abstractmethod
	def __call__(self, pkg):
		"""
		Check whether a package matches the condition specified in the matcher.

		@return: True if the package matches
		@rtype: bool
		"""
		pass

class PMKeywordMatcher(ABCObject):
	"""
	Base class for a keyword matcher.

	A keyword matcher is a condition passed as an keyword argument
	to the L{pkgset.PMPackageSet.filter()} function. It's basically an object
	which will be compared against metadata value using C{==} operator.
	"""

	@abstractmethod
	def __eq__(self, val):
		"""
		Check whether the value of a metadata key matches the condition
		specified in the matcher.
		
		@return: True if metadata value matches
		@rtype: bool
		"""
		pass
