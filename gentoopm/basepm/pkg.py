#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PMPackageSet(ABCObject):
	@abstractmethod
	def __iter__(self):
		"""
		Iterate over the packages (or sets) in a set.
		"""
		pass

	def filter(self, *args, **kwargs):
		"""
		Filter the packages based on arguments. Return a PMFilteredPackageSet
		evaluating to a number of PMPackages.

		The positional arguments can provide a number of PMPackageMatchers (see
		gentoopm.basepm.filter) and/or an atom string. The keyword arguments
		match metadata keys using '==' comparison with passed values (objects).

		Multiple filters will be AND-ed together. Same applies for .filter()
		called multiple times. You should, however, avoid passing multiple
		atoms as it is not supported by all PMs.

		This function can raise KeyError when a keyword argument does reference
		an incorrect metadata key.
		"""

		return PMFilteredPackageSet(iter(self), args, kwargs)

	@property
	def best(self):
		"""
		Return the best-matching package in the set (i.e. flatten it, sort
		the results and return the first one).
		"""
		try:
			return sorted(self, reverse = True)[0]
		except IndexError:
			raise TypeError('.best called on an empty set')
		except TypeError:
			raise KeyError('.best called on a set of differently-named packages')

	def select(self, *args, **kwargs):
		"""
		Select a single package matching keys in positional and keyword
		arguments. This is a convenience wrapper for filter(*args,
		**kwargs).best.
		"""
		try:
			return self.filter(*args, **kwargs).best
		except TypeError:
			raise KeyError('No packages match the filters.')
		except KeyError:
			raise ValueError('Ambiguous filter (matches more than a single package name).')

class PMFilteredPackageSet(PMPackageSet):
	def __init__(self, it, args, kwargs):
		self._iter = it
		self._args = args
		self._kwargs = kwargs

	def __iter__(self):
		for el in self._iter:
			if el._matches(*self._args, **self._kwargs):
				yield el

class PMPackage(ABCObject):
	"""
	An abstract class representing a single, uniquely-keyed package
	in the package tree.
	"""

	def _matches(self, *args, **kwargs):
		"""
		Check whether the package matches passed filters. Please note that this
		method may not be called at all if PM is capable of a more efficient
		filtering.

		If kwargs reference incorrect metadata keys, a KeyError will be raised.
		"""

		# XXX: apply filters

		for k, m in kwargs.items():
			try:
				v = self.metadata[k]
			except KeyError:
				raise KeyError('Unmatched keyword argument: %s' % k)
			else:
				if not m == v:
					return False

		return True

	@abstractproperty
	def id(self):
		"""
		Return an unique identifier for the package.
		"""
		pass

	@abstractproperty
	def path(self):
		"""
		Return path to the ebuild file (or vardb entry) if appropriate.
		If not available, just return None.
		"""
		pass

	@abstractproperty
	def metadata(self):
		"""
		Return PMPackageMetadata object for the package.
		"""
		pass

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, repr(self.id))
