#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, \
		PMEbuildRepository
from gentoopm.pkgcorepm.pkg import PkgCoreCategory
from gentoopm.util import IterDictWrapper

class PkgCoreRepoDict(PMRepositoryDict):
	def __iter__(self):
		for i, r in enumerate(self._stack.trees):
			yield PkgCoreEbuildRepo(r, i)

	def __init__(self, stack):
		self._stack = stack

class PkgCoreRepository(PMRepository):
	def __init__(self, repo_obj):
		self._repo = repo_obj

	def __iter__(self):
		for c in self._repo.categories:
			yield PkgCoreCategory(c, self)

	@property
	def categories(self):
		"""
		A convenience wrapper for the category list.
		"""
		return IterDictWrapper(self)

class PkgCoreEbuildRepo(PkgCoreRepository, PMEbuildRepository):
	def __init__(self, repo_obj, index):
		PkgCoreRepository.__init__(self, repo_obj)
		self._index = index

	@property
	def name(self):
		return self._repo.repo_id

	@property
	def path(self):
		return self._repo.location

	def __cmp__(self, other):
		return cmp(other._index, self._index)

class PkgCoreInstalledRepo(PkgCoreRepository):
	pass
