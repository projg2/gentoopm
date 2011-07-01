#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections, os.path

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict

class PaludisRepoDict(PMRepositoryDict):
	def __iter__(self):
		for l in self._shell.get_list('print-repositories',
				'--format', 'e'):
			yield PaludisRepository(l, self._shell)

	@property
	def master(self):
		return self['gentoo'] # XXX

	def __init__(self, shell):
		self._shell = shell

class PaludisRepository(PMRepository):
	def __init__(self, repo_name, shell):
		self._name = repo_name
		self._shell = shell

	@property
	def name(self):
		return self._name

	@property
	def path(self):
		return self._shell.get_metadata('print-repository-metadata',
				'location', self._name)
