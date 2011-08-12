#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod
from operator import attrgetter
import itertools

from ..util import ABCObject, FillMissingNotEqual

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

class PMKeywordMatcher(ABCObject, FillMissingNotEqual):
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

class SmartAttrGetter(object):
	"""
	A wrapper on attrgetter, supporting dots replaced by underscores. Uses the
	first package matched to distinguish between real underscores and dots.
	"""

	def __init__(self, key):
		self._k = key
		self._getter = None

	def __call__(self, obj):
		if self._getter is not None:
			return self._getter(obj)

		def get_variants(args):
			prev = None
			for a in args:
				if prev is not None:
					yield ('%s_' % prev, '%s.' % prev)
				prev = a
			else:
				yield (prev,)

		variants = itertools.product(*get_variants(self._k.split('_')))
		for v in variants:
			self._getter = attrgetter(''.join(v))
			try:
				return self._getter(obj)
			except AttributeError:
				pass
		else:
			raise KeyError('Invalid keyword argument: %s' % self._k)

class PMTransformedKeywordFilter(PMPackageMatcher):
	def __init__(self, key, val):
		self._getter = SmartAttrGetter(key)
		self._val = val

	def __call__(self, pkg):
		return self._val == self._getter(pkg)

def transform_keyword_filters(kwargs):
	"""
	Transform a number of keyword filters into positional args.

	@param kwargs: keyword arguments, as passed to L{PMPackageSet.filter()}
	@type kwargs: dict
	@return: positional arguments representing the keyword filters
	@rtype: tuple
	"""

	return tuple([PMTransformedKeywordFilter(k, v)
			for k, v in kwargs.items()])
