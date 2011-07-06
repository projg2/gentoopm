#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, \
		PMEbuildRepository
from gentoopm.paludispm.pkg import PaludisID

class PaludisRepoDict(PMRepositoryDict):
	def __iter__(self):
		for r in self._env.repositories:
			if r.format_key().parse_value() == 'e':
				yield PaludisLivefsRepository(r, self._env)

	def __init__(self, env):
		self._env = env

class PaludisEnumID(object):
	pass

class PaludisRepository(PMRepository):
	def __init__(self, env):
		self._env = env

	def __iter__(self):
		enum = PaludisEnumID()
		for i, p in enumerate(self._env[paludis.Selection.AllVersionsSorted(
				paludis.FilteredGenerator(
					paludis.Generator.InRepository(self._repo.name),
					paludis.Filter.All()))]):
			yield PaludisID(p, i, enum)

class PaludisStackRepo(PaludisRepository):
	def __iter__(self):
		enum = PaludisEnumID()
		for i, p in enumerate(self._env[paludis.Selection.AllVersionsSorted(
				paludis.FilteredGenerator(
					paludis.Generator.All(),
					paludis.Filter.SupportsInstallAction()))]):
			yield PaludisID(p, i, enum)

class PaludisLivefsRepository(PaludisRepository, PMEbuildRepository):
	def __init__(self, repo_obj, env):
		self._env = env
		self._repo = repo_obj

	@property
	def name(self):
		return str(self._repo.name)

	@property
	def path(self):
		return self._repo.location_key().parse_value()

class PaludisInstalledRepo(PaludisRepository):
	def __init__(self, env):
		self._env = env
		for r in env.repositories:
			if str(r.name) == 'installed': # XXX
				self._repo = r
				break
		else:
			raise Exception('Unable to find installed repository.')
