#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractmethod, abstractproperty

from gentoopm.basepm.atom import PMAtom
from gentoopm.basepm.environ import PMPackageEnvironment
from gentoopm.util import ABCObject, FillMissingComparisons

class PMPackageDescription(ABCObject):
	"""
	Description of a package.
	"""

	@abstractproperty
	def short(self):
		"""
		The short package description (e.g. C{DESCRIPTION} within the ebuild).

		@type: L{StringWrapper}
		"""
		pass

	@abstractproperty
	def long(self):
		"""
		The long package description (e.g. from C{metadata.xml}).

		@type: L{StringWrapper}/C{None}
		"""
		pass

	def __str__(self):
		"""
		Stringify to the best package description. In other words, long package
		description if available, short otherwise.

		@returns: best package description
		@rtype: string
		"""
		return self.long or self.short

class PMPackage(PMAtom, FillMissingComparisons):
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
	def id(self):
		"""
		An unique identifier for the package.

		@type: hashable
		@deprecated: use the package itself or its C{hash()} instead
		"""
		return self

	@property
	def atom(self):
		"""
		Return an atom matching the package uniquely.

		@type: L{PMAtom}
		@deprecated: the package is now a subclass of L{PMAtom}
			and can be used directly as an atom
		"""
		return self

	@abstractproperty
	def path(self):
		"""
		Path to the ebuild file (or vardb entry) if appropriate.

		This function may return C{None} if that information is not available
		or the particular repository doesn't operate on local filesystem.

		@type: L{StringWrapper}/C{None}
		"""
		pass

	@abstractproperty
	def metadata(self):
		"""
		The metadata accessor object for the package.

		@type: L{PMPackageMetadata}
		@deprecated: inconsistent, please use L{PMPackage} properties instead
		"""
		pass

	@abstractproperty
	def description(self):
		"""
		The description of the package.

		@type: L{PMPackageDescription}
		"""
		pass

	@abstractproperty
	def inherits(self):
		"""
		Eclasses inherited by a package.

		@type: tuple(L{StringWrapper})/C{None}
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

		if self.path is None:
			return None
		p = str(self.path)

		if os.path.isdir(p):
			def _mtime_if_exists(path):
				try:
					return os.path.getmtime(path)
				except OSError:
					return -1

			files = ('environment.bz2', 'environment')
			# Take the newer one.
			fn = sorted(files, key=_mtime_if_exists, reverse=True)[0]
			p = os.path.join(p, fn)

		if not os.path.exists(p):
			return None
		return PMPackageEnvironment(p)

	@abstractproperty
	def slotted(self):
		"""
		Return an atom matching all packages in the same slot as the associated
		package.

		This method should be used on associated atoms only. When called
		on an unassociated atom, it should raise an exception.

		@type: L{PMAtom}
		"""
		pass

	@abstractproperty
	def unversioned(self):
		"""
		Return an atom matching all packages with the same key as the
		associated package.

		This method should be used on associated atoms only. When called
		on an unassociated atom, it should raise an exception.

		@type: L{PMAtom}
		"""
		pass

	@abstractmethod
	def __lt__(self, other):
		pass

	# atom API

	def __contains__(self, pkg):
		return self == pkg

	@property
	def complete(self):
		return True

	@property
	def associated(self):
		return True
