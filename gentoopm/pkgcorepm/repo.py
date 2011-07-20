#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pkgcore.restrictions.boolean as br

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, \
		PMEbuildRepository
from gentoopm.pkgcorepm.pkg import PkgCorePackage, PkgCorePackageSet, \
		PkgCoreFilteredPackageSet
from gentoopm.pkgcorepm.filter import transform_filters
from gentoopm.util import FillMissingComparisons

class PkgCoreRepoDict(PMRepositoryDict):
	def __iter__(self):
		for i, r in enumerate(self._stack.trees):
			yield PkgCoreEbuildRepo(r, i)

	def __init__(self, stack):
		self._stack = stack

class PkgCoreRepository(PkgCorePackageSet, PMRepository):
	_index = 0
	def __init__(self, repo_obj):
		self._repo = repo_obj

	def __iter__(self):
		index = self._index
		for pkg in self._repo:
			yield PkgCorePackage(pkg, index)

	def filter(self, *args, **kwargs):
		r = self
		filt, newargs, newkwargs = transform_filters(args, kwargs)

		if filt:
			r = PkgCoreFilteredRepo(self, filt)
		if newargs or newkwargs:
			r = PkgCoreFilteredPackageSet(r, args, kwargs)

		return r

class PkgCoreFilteredRepo(PkgCoreRepository):
	def __init__(self, repo, filt):
		self._repo = repo
		self._filt = filt
		self._index = repo._index

	def __iter__(self):
		index = self._index
		for pkg in self._repo._repo.match(self._filt):
			yield PkgCorePackage(pkg, index)

	def filter(self, *args, **kwargs):
		r = self
		filt, newargs, newkwargs = transform_filters(args, kwargs)

		if filt:
			r = PkgCoreFilteredRepo(self._repo,
					br.AndRestriction(self._filt, filt))
		if newargs or newkwargs:
			r = PkgCoreFilteredPackageSet(r, args, kwargs)

		return r

class PkgCoreEbuildRepo(PkgCoreRepository, PMEbuildRepository,
		FillMissingComparisons):

	def __init__(self, repo_obj, index):
		PkgCoreRepository.__init__(self, repo_obj)
		self._index = index

	@property
	def name(self):
		return self._repo.repo_id

	@property
	def path(self):
		return self._repo.location

	def __lt__(self, other):
		return other._index < self._index

class PkgCoreInstalledRepo(PkgCoreRepository):
	pass
