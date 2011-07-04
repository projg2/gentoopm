#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections, os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, \
		PMEbuildRepository
from gentoopm.paludispm.pkg import PaludisCategory
from gentoopm.util import IterDictWrapper

class PaludisRepoDict(PMRepositoryDict):
	def __iter__(self):
		for r in self._env.repositories:
			if r.format_key().parse_value() == 'e':
				yield PaludisLivefsRepository(r)

	def __init__(self, env):
		self._env = env

class PaludisRepository(PMRepository):
	def __iter__(self):
		for c in self._repo.category_names([]):
			pc = PaludisCategory(c, self)
			try:
				next(iter(pc))
			except StopIteration: # omit empty categories
				pass
			else:
				yield pc

	@property
	def categories(self):
		"""
		A convenience wrapper for the category list.
		"""
		return IterDictWrapper(self)

class PaludisLivefsRepository(PaludisRepository, PMEbuildRepository):
	def __init__(self, repo_obj):
		self._repo = repo_obj

	@property
	def name(self):
		return str(self._repo.name)

	@property
	def path(self):
		return self._repo.location_key().parse_value()

class PaludisInstalledRepo(PaludisRepository):
	def __init__(self, env):
		for r in env.repositories:
			if str(r.name) == 'installed': # XXX
				self._repo = r
				break
		else:
			raise Exception('Unable to find installed repository.')
