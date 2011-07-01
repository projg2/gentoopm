#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os, os.path
from portage import create_trees

from gentoopm.basepm import PackageManager, PMRepositoryDict
from gentoopm.portagepm.repo import PortDBRepository

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

class PortagePM(PackageManager):
	name = 'portage'

	def reload_config(self):
		# Similarly to emerge, care for PORTAGE_CONFIGROOT and ROOT.
		trees = create_trees(
				config_root = os.environ.get('PORTAGE_CONFIGROOT'),
				target_root = os.environ.get('ROOT'))
		tree = trees[max(trees)]
		self._vardb = tree['vartree'].dbapi
		self._portdb = tree['porttree'].dbapi

	@property
	def repositories(self):
		return PortageRepoDict(self._portdb)
