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
		Filter the packages based on keys passed as arguments. Positional
		arguments refer to keys by their level (with first arg being the
		top-level key), None means match-all. Keyword arguments refer to keys
		by their names.

		If an argument doesn't match any key (i.e. too many args are passed),
		a KeyError or IndexError will be raised. If the same key is referred
		through positional and keyword arguments, a TypeError will be raised.

		The filtering will result in an iterable of PMKeyedPackageDicts
		or PMPackages, depending on whether the filtering criteria are able
		to uniquely identify packages.

		The '==' operator is used to match packages. To extend matching, you
		can provide a class with __eq__() redefined as an argument.
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
			for x in el.filter(*self._args, **self._kwargs):
				yield x

class PMPackage(ABCObject):
	"""
	An abstract class representing a single, uniquely-keyed package
	in the package tree.
	"""

	def filter(self, **kwargs):
		"""
		Filter packages on metadata. This is mostly to extend superclass
		.filter() method.

		If args are non-empty, raises an IndexError (unused args). If kwargs
		contains keys not matching metadata, raises a KeyError. Otherwise,
		returns an iterator -- either over the package itself or an empty one.
		"""

		for k, m in kwargs.items():
			try:
				v = self.metadata[k]
			except KeyError:
				raise KeyError('Unmatched keyword argument: %s' % k)
			else:
				if not m == v:
					return

		yield self

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
