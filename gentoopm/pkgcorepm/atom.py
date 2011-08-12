#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.ebuild.atom import atom
from pkgcore.ebuild.restricts import PackageDep, VersionMatch, \
		RepositoryDep, SlotDep
from pkgcore.restrictions.boolean import AndRestriction
from pkgcore.util.parserestrict import parse_match, ParseError

from ..basepm.atom import PMAtom, PMPackageKey, PMPackageVersion, \
		PMIncompletePackageKey
from ..exceptions import InvalidAtomStringError

def _find_res(res, cls):
	if isinstance(res, AndRestriction):
		restrictions = res.restrictions
	else:
		restrictions = (res,)

	for r in restrictions:
		if isinstance(r, cls):
			return r
	else:
		return None

class PkgCorePackageKey(PMPackageKey):
	def __init__(self, atom):
		self._atom = atom

	@property
	def category(self):
		return self._atom.category

	@property
	def package(self):
		return self._atom.package

	def __str__(self):
		return self._atom.key

class PkgCoreIncompletePackageKey(PMIncompletePackageKey):
	def __init__(self, r):
		self._r = _find_res(r, PackageDep)
		if self._r is None:
			raise AssertionError('No PackageDep in restrictions.')

	@property
	def package(self):
		return self._r.restriction.exact

class PkgCorePackageVersion(PMPackageVersion):
	def __init__(self, atom):
		if atom.version is None:
			raise AssertionError('Empty version in atom')
		self._atom = atom

	@property
	def without_revision(self):
		return self._atom.version

	@property
	def revision(self):
		return self._atom.revision or 0

	def __str__(self):
		return self._atom.fullver

	def __lt__(self, other):
		if self._atom.key != other._atom.key:
			raise NotImplementedError('Unable to compare versions of distinct packages')
		return self._atom < other._atom

class PkgCoreIncompletePackageVersion(PMPackageVersion):
	def __init__(self, r):
		self._r = _find_res(r, VersionMatch)
		if self._r is None:
			raise AssertionError('No VersionMatch in restrictions.')

	@property
	def without_revision(self):
		return self._r.ver

	@property
	def revision(self):
		return self._r.rev or 0

	def __lt__(self, other):
		raise NotImplementedError('Unable to compare versions of incomplete atoms')

	def __str__(self):
		# XXX: ugly?
		return str(self._r).split()[-1]

class PkgCoreAtom(PMAtom):
	def __init__(self, s):
		if isinstance(s, atom):
			self._r = s
		else:
			try:
				self._r = parse_match(s)
			except ParseError:
				raise InvalidAtomStringError('Incorrect atom: %s' % s)

	def __contains__(self, pkg):
		return self._r.match(pkg._pkg) != self.blocking

	def __str__(self):
		if self.complete:
			return str(self._r)
		else:
			raise ValueError('Unable to stringify incomplete atom')

	@property
	def complete(self):
		return isinstance(self._r, atom)

	@property
	def blocking(self):
		# incomplete atoms can't block
		return self.complete and self._r.blocks

	@property
	def key(self):
		if self.complete:
			return PkgCorePackageKey(self._r)
		else:
			return PkgCoreIncompletePackageKey(self._r)

	@property
	def version(self):
		try:
			if self.complete:
				return PkgCorePackageVersion(self._r)
			else:
				return PkgCoreIncompletePackageVersion(self._r)
		except AssertionError:
			return None

	@property
	def slot(self):
		if self.complete:
			return self._r.slot[0] if self._r.slot \
					else None
		else:
			r = _find_res(self._r, SlotDep)
			return r.restriction.exact if r is not None \
					else None

	@property
	def repository(self):
		if self.complete:
			return self._r.repo_id
		else:
			r = _find_res(self._r, RepositoryDep)
			return r.restriction.exact if r is not None \
					else None
