#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict

class PkgCoreRepoDict(PMRepositoryDict):
	def __iter__(self):
		for k in self._config.repo:
			if os.path.isabs(k):
				yield PkgCoreRepository(self._config.repo[k])

	def __init__(self, config):
		self._config = config

class PkgCoreRepository(PMRepository):
	def __init__(self, repo_obj):
		self._repo = repo_obj

	@property
	def name(self):
		return self._repo.repo_id

	@property
	def path(self):
		return self._repo.location
