#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage
from gentoopm.basepm.repo import PMRepository

class PMPackageWrapper(PMPackage):
	key_name = 'REPOSITORY'

	def __init__(self, wrapped, parent):
		self._wrapped = wrapped
		self._parent = parent

	@property
	def metadata(self):
		return self._wrapped.metadata

	@property
	def key(self):
		p = self._wrapped.parent
		while p.key_name != 'REPOSITORY':
			p = p.parent
		return p.key

class PMStackWrapper(PMKeyedPackageDict):
	def __init__(self, wrapped, parent):
		self._wrapped = wrapped
		self._parent = parent

	def __iter__(self):
		keys = collections.defaultdict(list)
		for r in self._wrapped:
			if isinstance(r, PMPackage):
				yield PMPackageWrapper(r, self)
			else:
				for wr in r:
					keys[wr.key].append(wr)
		for k, l in keys.items():
			yield PMStackWrapper(l, self)

	@property
	def key(self):
		try:
			return self._wrapped[0].key
		except IndexError:
			return None

	@property
	def key_name(self):
		try:
			return self._wrapped[0].key_name
		except IndexError:
			return None

class PMRepoStackWrapper(PMStackWrapper, PMRepository):
	def __init__(self, repos):
		self._wrapped = repos

	@property
	def key(self):
		return None

	@property
	def key_name(self):
		return None

	@property
	def parent(self):
		return None
