#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from gentoopm.basepm.repo import PMRepositoryDict, PMEbuildRepository, \
		PMRepository
from gentoopm.portagepm.pkg import PortageCPV, PortageDBCPV, PortagePackageSet

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

class PortDBRepository(PortagePackageSet, PMRepository):
	def __init__(self, dbapi):
		self._dbapi = dbapi

	def __iter__(self):
		for p in self._dbapi.cpv_all(): # XXX
			yield PortageDBCPV(p, self._dbapi)

class PortageRepository(PortDBRepository, PMEbuildRepository):
	def __init__(self, repo_obj, portdbapi):
		self._repo = repo_obj
		PortDBRepository.__init__(self, portdbapi)

	def __iter__(self):
		path = self.path
		prio = self._repo.priority
		for cp in self._dbapi.cp_all(trees = (path,)):
			for p in self._dbapi.cp_list(cp, mytree = path):
				yield PortageCPV(p, self._dbapi, path, prio)

	@property
	def name(self):
		return self._repo.name

	@property
	def path(self):
		return self._repo.location

	def __cmp__(self, other):
		return cmp(self._repo.priority, other._repo.priority)

class VDBRepository(PortDBRepository):
	pass
