#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage, PMPackageDescription, \
		PMInstallablePackage, PMInstalledPackage
from gentoopm.paludispm.atom import PaludisAtom, \
		PaludisPackageKey, PaludisPackageVersion
from gentoopm.util import SpaceSepTuple

class PaludisPackageDescription(PMPackageDescription):
	def __init__(self, pkg):
		self._pkg = pkg

	@property
	def short(self):
		return self._pkg.short_description_key().parse_value()

	@property
	def long(self):
		k = self._pkg.long_description_key()
		return k.parse_value() if k is not None else None

class PaludisID(PMPackage, PaludisAtom):
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
	def slotted(self):
		cp = str(self.key)
		slot = self.slot
		return PaludisAtom('%s:%s' % (cp, slot), self._env)

	@property
	def unversioned(self):
		return PaludisAtom(str(self.key), self._env)

	@property
	def key(self):
		return PaludisPackageKey(self._pkg.name)

	@property
	def version(self):
		return PaludisPackageVersion(self._pkg.version)

	@property
	def description(self):
		return PaludisPackageDescription(self._pkg)

	@property
	def inherits(self):
		k = self._pkg.find_metadata('INHERITED')
		if k is None:
			return SpaceSepTuple(())
		return SpaceSepTuple(k.parse_value())

	@property
	def homepages(self):
		spec = self._pkg.homepage_key().parse_value()
		return SpaceSepTuple([str(x) for x in spec])

	@property
	def slot(self):
		k = self._pkg.slot_key()
		return str(k.parse_value())

	@property
	def repository(self):
		return str(self._pkg.repository_name)

	@property
	def _atom(self):
		return self._pkg.uniquely_identifying_spec()

	def __str__(self):
		return str(self._atom)

	def __lt__(self, other):
		if not isinstance(other, PaludisID):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		if self._enum_id != other._enum_id:
			raise TypeError('Unable to compare results of two enumerations')
		return self._num < other._num

class PaludisInstallableID(PaludisID, PMInstallablePackage):
	pass

class PaludisInstalledID(PaludisID, PMInstalledPackage):
	pass

class PaludisMetadata(PMPackageMetadata):
	def __init__(self, pkg):
		self._pkg = pkg

	def __getattr__(self, key):
		"""
		Get the value of a metadata key through an attribute.

		@param key: the metadata key to catch
		@type key: string
		@return: the value of a metadata key, or C{''} when unset
		@rtype: string
		@raise AttributeError: when invalid metadata key referred
		@raise NotImplementedError: when not-stringifiable key referred
		@bug: not all values can be stringified, pretty printing API
			hasn't been wrapped in Python yet
		"""
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
