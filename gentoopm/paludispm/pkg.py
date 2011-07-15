#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage
from gentoopm.paludispm.atom import PaludisAtom

class PaludisID(PMPackage):
	def __init__(self, pkg, num = 0, enum_id = None, env = None):
		self._pkg = pkg
		self._num = num
		self._enum_id = enum_id
		self._env = env

	@property
	def metadata(self):
		return PaludisMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.fs_location_key().parse_value()

	@property
	def atom(self):
		return PaludisAtom(self._pkg.uniquely_identifying_spec(),
				self._env, self)

	def __lt__(self, other):
		if not isinstance(other, PaludisID):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if self._enum_id != other._enum_id:
			raise TypeError('Unable to compare results of two enumerations')
		return self._num < other._num

class PaludisMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	def __getattr__(self, key):
		if key not in self:
			raise AttributeError('Unsupported metadata key: %s' % key)
		m = self._pkg.find_metadata(key)
		if m is None:
			return ''
		m = m.parse_value()
		if isinstance(m, paludis.StringSetIterable) \
				or isinstance(m, paludis.KeywordNameIterable):
			return ' '.join([str(x) for x in m])
		elif isinstance(m, paludis.AllDepSpec):
			raise NotImplementedError('Parsing %s is not supported yet.' % key)
		else:
			return str(m)
