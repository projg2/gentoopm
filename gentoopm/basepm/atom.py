#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PMPackageKey(ABCObject):
	"""
	A base class for a package key (CP/qualified package name).
	"""

	@abstractproperty
	def category(self):
		"""
		The package category.

		@type: string/C{None}
		"""
		pass

	@abstractproperty
	def package(self):
		"""
		The package name.

		@type: string
		"""
		pass

	@abstractmethod
	def __str__(self):
		"""
		Return the stringified package key.

		@return: Stringified package key.
		@rtype: string
		"""
		pass

	def __eq__(self, other):
		return str(self) == str(other)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(str(self))

class PMIncompletePackageKey(PMPackageKey):
	"""
	An incomplete package key (without a category).

	This is just a helper class to simplify implementations. You should not
	rely on this particular class being used, implementations are free to
	implement incomplete keys using plain L{PMPackageKey}.
	"""

	@property
	def category(self):
		return None

	def __str__(self):
		return self.package

class PMPackageVersion(ABCObject):
	"""
	A base class for a package version.
	"""

	@abstractproperty
	def without_revision(self):
		"""
		The actual package version.

		@type: string
		"""
		pass

	@abstractproperty
	def revision(self):
		"""
		The ebuild revision.

		@type: int
		"""
		pass

	@abstractmethod
	def __str__(self):
		"""
		Return the stringified package version.

		@return: Stringified package version.
		@rtype: string
		"""
		pass

	def __eq__(self, other):
		return str(self) == str(other)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		return hash(str(self))

class PMAtom(ABCObject):
	"""
	A base class for PM-specific atom (dependency specification).
	"""

	@abstractmethod
	def __init__(self, s):
		"""
		Create a new atom from string.

		@param s: atom-formatted string
		@type s: string
		"""
		pass

	@abstractmethod
	def __contains__(self, pkg):
		"""
		Check whether a package matches the atom (is contained in the set
		of packages matched by atom).

		@param pkg: a package to match
		@type pkg: L{PMPackage}
		"""
		pass

	@abstractmethod
	def __str__(self):
		"""
		Return the string representation of the atom.

		If the atom is incomplete (misses a category), the result is undefined.
		It can raise an exception then.
		"""
		pass

	def __eq__(self, other):
		if not self.complete:
			raise NotImplementedError('Unable to compare incomplete atoms')
		return str(self) == str(other)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __hash__(self):
		if not self.complete:
			raise NotImplementedError('Unable to hash incomplete atoms')
		return hash(str(self))

	def __repr__(self):
		if self.complete:
			s = repr(self.__str__())
		else:
			s = '<incomplete>'
		return '%s(%s)' % (self.__class__.__name__, s)

	@abstractproperty
	def complete(self):
		"""
		Whether the atom is complete, i.e. whether the category is specified.

		If an atom is incomplete, it is impossible to stringify it. Using such
		an atom with L{pkgset.PMPackageSet.select()} may result
		in an L{AmbiguousPackageSetError}.

		@type: bool
		"""
		pass

	@abstractproperty
	def associated(self):
		"""
		Whether the atom is associated with a package.

		If an atom is unassociated, it is impossible to transform it.

		@type: bool
		"""
		pass

	def get_associated(self, repo):
		"""
		Return an atom associated with a matching package in the repository.

		@param repo: Repository to find a match in.
		@type repo: L{PMRepository}
		@return: An associated atom.
		@rtype: L{PMAtom}
		@raise EmptyPackageSetError: when no packages match the atom
		@raise AmbiguousPackageSetError: when packages with different keys
			match the atom
		"""
		return repo.select(self).atom

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

	@abstractproperty
	def key(self):
		"""
		The package key.

		@type: L{PMPackageKey}
		"""
		pass

	@abstractproperty
	def version(self):
		"""
		The package version.

		@type: L{PMPackageVersion}/C{None}
		"""
		pass
