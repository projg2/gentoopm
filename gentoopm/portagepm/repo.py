#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict

class PortageRepoDict(PMRepositoryDict):
	def __iter__(self):
		for repo_name in self._dbapi.getRepositories():
			yield PortDBRepository(repo_name, self._dbapi)

	def __getitem__(self, key):
		if os.path.isabs(key):
			repo_name = self._dbapi.getRepositoryName(key)
		else:
			repo_name = key
		try:
			return PortDBRepository(repo_name, self._dbapi)
		except KeyError:
			raise KeyError('No repository matched key %s' % key)

	def __init__(self, portdbapi):
		self._dbapi = portdbapi

class PortDBRepository(PMRepository):
	def __init__(self, repo_name, portdbapi):
		self._name = repo_name
		self._dbapi = portdbapi
		# Check if repo_name is correct
		self.path

	def __repr__(self):
		return '%s(%s, %s)' % (
				self.__class__.__name__,
				repr(self._name),
				repr(self._dbapi))

	@property
	def name(self):
		return self._name

	@property
	def path(self):
		p = self._dbapi.getRepositoryPath(self._name)
		if not p:
			raise KeyError('Failed to access repository %s' % self._name)
		return p
