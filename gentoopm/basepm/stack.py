#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import collections

from gentoopm.basepm.pkg import PMKeyedPackageDict, PMPackage
from gentoopm.basepm.repo import PMRepository

class PMPackageWrapper(PMPackage):
	_key_name = 'REPOSITORY'

	def __init__(self, wrapped, parent):
		self._wrapped = wrapped
		self._parent_ = parent

	@property
	def metadata(self):
		return self._wrapped.metadata

	@property
	def _key(self):
		return self._repo._key

	@property
	def _repo(self):
		p = self._wrapped._parent
		while p._key_name != 'REPOSITORY':
			p = p._parent
		return p

	@property
	def path(self):
		return self._wrapped.path

	def __cmp__(self, other):
		r = cmp(self._wrapped, other._wrapped)
		if r == 0:
			return cmp(self._repo, other._repo)
		return r

class PMStackWrapper(PMKeyedPackageDict):
	def __init__(self, wrapped, parent):
		self._wrapped = wrapped
		self._parent_ = parent

	def __iter__(self):
		keys = collections.defaultdict(list)
		for r in self._wrapped:
			if isinstance(r, PMPackage):
				yield PMPackageWrapper(r, self)
			else:
				for wr in r:
					keys[wr._key].append(wr)
		for k, l in keys.items():
			yield PMStackWrapper(l, self)

	@property
	def _key(self):
		try:
			return self._wrapped[0]._key
		except IndexError:
			return None

	@property
	def _key_name(self):
		try:
			return self._wrapped[0]._key_name
		except IndexError:
			return None

class PMRepoStackWrapper(PMStackWrapper, PMRepository):
	_key_name = None
	_key = None
	_parent = None

	def __init__(self, repos):
		self._wrapped = repos
