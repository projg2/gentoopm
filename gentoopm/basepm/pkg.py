#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractproperty

from gentoopm.basepm.atom import PMAtom
from gentoopm.basepm.environ import PMPackageEnvironment
from gentoopm.util import ABCObject

class PMPackage(ABCObject):
	"""
	An abstract class representing a single, uniquely-identified package
	in the package tree.
	"""

	def _matches(self, *args, **kwargs):
		"""
		Check whether the package matches passed filters. Please note that this
		method may not be called at all if PM is capable of a more efficient
		filtering.

		@param args: list of package matchers
		@type args: list(L{PMPackageMatcher},L{PMAtom})
		@param kwargs: dict of keyword matchers
		@type kwargs: dict(string -> L{PMKeywordMatcher})
		@return: True if package matches
		@rtype: bool
		@raise KeyError: when invalid metadata key is referenced in kwargs
		"""

		for f in args:
			if callable(f): # a matcher
				if not f(self):
					return False
			elif isinstance(f, PMAtom): # an atom
				if not self in f:
					return False
			else:
				raise ValueError('Incorrect positional argument: %s' % f)

		for k, m in kwargs.items():
			try:
				v = self.metadata[k]
			except KeyError:
				raise KeyError('Unmatched keyword argument: %s' % k)
			else:
				if not m == v:
					return False

		return True

	@property
	def key(self):
		"""
		The key identifying the package. This is used to group packages, e.g.
		when choosing the best package in a set.

		@type: hashable
		"""
		return self.atom.key

	@property
	def id(self):
		"""
		An unique identifier for the package.

		@type: hashable
		"""
		return self.atom

	@abstractproperty
	def atom(self):
		"""
		Return an atom matching the package uniquely.

		@type: L{PMAtom}
		"""
		pass

	@abstractproperty
	def path(self):
		"""
		Path to the ebuild file (or vardb entry) if appropriate.

		This function may return C{None} if that information is not available
		or the particular repository doesn't operate on local filesystem.

		@type: string/C{None}
		"""
		pass

	@abstractproperty
	def metadata(self):
		"""
		The metadata accessor object for the package.

		@type: L{PMPackageMetadata}
		"""
		pass

	@property
	def environ(self):
		"""
		The environment accessor object for the package.

		Please note that this function may return C{None} if environment is
		inaccessible (path is unavailable or file does not exist).

		@type: L{PMPackageEnvironment}/C{None}
		"""

		p = self.path
		if p is None:
			return None

		if os.path.isdir(p):
			# XXX: look for .bz2 and plain, take the newer one
			p = os.path.join(p, 'environment.bz2')

		if not os.path.exists(p):
			return None
		return PMPackageEnvironment(p)

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return self.id == other.id

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, repr(self.id))
