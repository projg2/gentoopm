#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections, os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict

class PaludisRepoDict(PMRepositoryDict):
	def __iter__(self):
		for r in self._env.repositories:
			if r.format_key().parse_value() == 'e':
				yield PaludisRepository(r)

	def __init__(self, env):
		self._env = env

class PaludisRepository(PMRepository):
	def __init__(self, repo_obj):
		self._repo = repo_obj

	@property
	def name(self):
		return str(self._repo.name)

	@property
	def path(self):
		return self._repo.location_key().parse_value()
