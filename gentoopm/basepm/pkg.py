#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections
from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PMKeyedPackageBase(ABCObject):
	"""
	Base class for key-identified package sets.
	"""

	def __init__(self, key, parent):
		self._key = key
		self._parent = parent

	@property
	def parent(self):
		"""
		A parent (higher level) PMKeyedPackageDict or None if top-level.
		"""
		return self._parent

	@property
	def key(self):
		"""
		The key for this level of PMKeyedPackageDict.
		"""
		return self._key

	@abstractproperty
	def key_name(self):
		"""
		The metadata key name for this key.
		"""
		pass

	@property
	def keys(self):
		"""
		The set of keys uniquely identifying the package set (i.e. the parent
		keys and this one).
		"""
		key_names = []
		keys = []
		o = self
		while o:
			keys.insert(0, o.key)
			key_names.insert(0, o.key_name)
			o = o.parent
		t = collections.namedtuple('%sKeyTuple' % self.__class__.__name__,
				' '.join(key_names))
		return t(*keys)

class PMKeyedPackageDict(PMKeyedPackageBase):
	"""
	A dict-like object representing a set of packages matched by a N-level key.
	If it's a last-level key, the dict evaluates to PMPackage subclass
	instances. Otherwise, it evaluates to lower-level PMKeyedPackageDicts.

	Usually, the highest level PMKeyedPackageDict is PMRepository. Then dicts
	refer to the category, package name and finally version (where they
	transform into PMPackages).
	"""

	@abstractmethod
	def __iter__(self):
		"""
		Iterate over child PMKeyedPackageDicts or PMPackages when bottom-level.
		"""
		pass

	def __getitem__(self, key):
		"""
		Get a sub-item matching the key.
		"""
		for i in self:
			if i.key == key:
				return i
		else:
			raise KeyError('No packages match keyset: (%s)' % \
					', '.join(self.keys + [key]))

	@property
	def flattened(self):
		"""
		Flatten the package set and iterate over it. Yield PMPackages.
		"""

		for i in self:
			if isinstance(i, PMKeyedPackageDict):
				for hi in i.flattened:
					yield hi
			else:
				yield i

class PMPackage(PMKeyedPackageBase):
	"""
	An abstract class representing a single, uniquely-keyed package
	in the package tree.
	"""
	pass
