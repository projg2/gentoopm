#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.repo import PMRepository

class PMRepoStackWrapper(PMRepository):
	def __init__(self, repos):
		self._repos = repos

	def __iter__(self):
		for r in self._repos:
			for p in r:
				yield p
