#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractmethod, abstractproperty

from gentoopm.basepm.atom import PMAtom, PMPackageKey
from gentoopm.basepm.environ import PMPackageEnvironment
from gentoopm.util import ABCObject, FillMissingComparisons, StringCompat, \
		EnumTuple

PMPackageState = EnumTuple('PMPackageState',
		'installable',
		'installed')

class PMBoundPackageKey(PMPackageKey):
	"""
	A package key bound to a specific package.
	"""

	@abstractproperty
	def state(self):
		"""
		State of the bound package.

		@type: L{PMPackageState}
		"""
		pass

	def __eq__(self, other):
		if isinstance(other, PMBoundPackageKey) and not self.state == other.state:
			return False
		return PMPackageKey.__eq__(self, other)

	def __hash__(self):
		return hash((str(self), self.state))

class PMPackageDescription(ABCObject, StringCompat):
	"""
	Description of a package.
	"""

	@abstractproperty
	def short(self):
		"""
		The short package description (e.g. C{DESCRIPTION} within the ebuild).

		@type: string
		"""
		pass

	@abstractproperty
	def long(self):
		"""
		The long package description (e.g. from C{metadata.xml}).

		@type: string/C{None}
		"""
		pass

	def __str__(self):
		"""
		Stringify to the best package description. In other words, long package
		description if available, short otherwise.

		@returns: best package description
		@rtype: string
		"""
		return str(self.long or self.short)

class PMUseFlag(ABCObject, StringCompat):
	"""
	A base class for a USE flag supported by a package.
	"""

	def __init__(self, usestr):
		"""
		Instantiate from an IUSE atom.

		@param usestr: the IUSE atom (C{[+-]?flag})
		@type usestr: string
		"""
		self._name = usestr.lstrip('+-')

	@property
	def name(self):
		"""
		The flag name.

		@type: string
		"""
		return self._name

	@abstractproperty
	def enabled(self):
		"""
		Whether the flag is enabled.

		@type: bool
		"""
		pass

	def __str__(self):
		return self.name

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
			if isinstance(f, PMAtom): # an atom
				if not self in f:
					return False
			elif hasattr(f, '__call__'):
				if not f(self):
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

		@type: string/C{None}
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
	def eapi(self):
		"""
		The EAPI used by the ebuild.

		@type: string
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

		@type: L{SpaceSepFrozenSet}
		"""
		pass

	@abstractproperty
	def defined_phases(self):
		"""
		List of phase functions declared by a package, if available.
		C{None} otherwise. Empty L{SpaceSepFrozenSet} means no phase function
		is declared.

		@type: L{SpaceSepFrozenSet}/C{None}
		"""
		pass

	@abstractproperty
	def homepages(self):
		"""
		Homepages of a package.

		@type: L{SpaceSepTuple}
		"""
		pass

	@abstractproperty
	def keywords(self):
		"""
		Package keywords.

		@type: L{SpaceSepFrozenSet}
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
	def build_dependencies(self):
		"""
		Get the package build dependencies (C{DEPEND}).

		@type: L{PMPackageDepSet}
		"""
		pass

	@abstractproperty
	def run_dependencies(self):
		"""
		Get the package runtime dependencies (C{RDEPEND}).

		@type: L{PMPackageDepSet}
		"""
		pass

	@abstractproperty
	def post_dependencies(self):
		"""
		Get the package post-installed dependencies (C{PDEPEND}).

		@type: L{PMPackageDepSet}
		"""
		pass

	@abstractproperty
	def use(self):
		"""
		Get the list of USE flags applying to the ebuild. Iterating over the
		list should return only the explicitly listed flags (C{IUSE}), though
		it is also possible to explicitly get other flags (using indexing)
		applying to the ebuild.

		@type: L{SpaceSepFrozenSet}(L{PMUseFlag})
		"""
		pass

	@abstractproperty
	def required_use(self):
		"""
		Get the C{REQUIRED_USE} specification.

		@type: L{PMPackageDepSet}
		"""
		pass

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
	def blocking(self):
		return False

	@property
	def associated(self):
		return True

class PMInstallablePackage(PMPackage):
	"""
	An abstract class for a package which can be installed.
	"""
	pass

class PMInstalledPackage(PMPackage):
	"""
	An abstract class for a installed package.
	"""

	@abstractproperty
	def contents(self):
		"""
		Return package contents list accessor.

		@type: L{PMPackageContents}
		"""
		pass
