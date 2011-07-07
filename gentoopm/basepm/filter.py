#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod

from gentoopm.util import ABCObject

class PMPackageMatcher(ABCObject):
	"""
	Base class for a package matcher.
	"""

	@abstractmethod
	def __call__(self, pkg):
		"""
		Check whether a package matches the condition specified in the matcher.
		Return True if it does, False otherwise.
		"""
		pass

class PMKeywordMatcher(ABCObject):
	"""
	Base class for a keyword matcher (one passed as a keyword argument
	instead of a plain string).
	"""

	@abstractmethod
	def __eq__(self, val):
		"""
		Check whether the value of a metadata key matches the condition
		specified in the matcher. Return True if it does, False otherwise.
		"""
		pass
