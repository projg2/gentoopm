#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, PMEbuildRepository
from gentoopm.portagepm.db import PortDBRepository
from gentoopm.portagepm.pkg import PortageCategory
from gentoopm.util import IterDictWrapper

class PortageRepoDict(PMRepositoryDict):
	def __iter__(self):
		for p_repo in self._dbapi.repositories:
			yield PortageRepository(p_repo, self._dbapi)

	def __getitem__(self, key):
		try:
			if os.path.isabs(key):
				repo_name = self._dbapi.repositories.get_name_for_location(key)
			else:
				repo_name = key
			r = self._dbapi.repositories[repo_name]
		except KeyError:
			raise KeyError('No repository matched key %s' % key)
		else:
			return PortageRepository(r, self._dbapi)

	def __init__(self, portdbapi):
		self._dbapi = portdbapi

class PortageRepository(PortDBRepository, PMEbuildRepository):
	def __init__(self, repo_obj, portdbapi):
		self._repo = repo_obj
		PortDBRepository.__init__(self, portdbapi)

	@property
	def name(self):
		return self._repo.name

	@property
	def path(self):
		return self._repo.location

	def __cmp__(self, other):
		return cmp(self._repo.priority, other._repo.priority)

	_category_class = PortageCategory
