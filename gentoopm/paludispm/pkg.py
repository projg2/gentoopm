#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.depend import PMRequiredUseAtom
from gentoopm.basepm.metadata import PMPackageMetadata
from gentoopm.basepm.pkg import PMPackage, PMPackageDescription, \
		PMInstallablePackage, PMInstalledPackage, PMBoundPackageKey, \
		PMPackageState, PMUseFlag
from gentoopm.paludispm.atom import PaludisAtom, \
		PaludisPackageKey, PaludisPackageVersion
from gentoopm.paludispm.contents import PaludisPackageContents
from gentoopm.paludispm.depend import PaludisPackageDepSet
from gentoopm.util import SpaceSepFrozenSet, SpaceSepTuple

class PaludisBoundPackageKey(PaludisPackageKey, PMBoundPackageKey):
	def __init__(self, key, pkg):
		PaludisPackageKey.__init__(self, key)
		self._state = PMPackageState(
				installable = isinstance(pkg, PaludisInstallableID),
				installed = isinstance(pkg, PaludisInstalledID))

	@property
	def state(self):
		return self._state

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

class PaludisChoice(PMUseFlag):
	def __init__(self, choice):
		self._c = choice

	@property
	def name(self):
		return str(self._c.name_with_prefix)

	@property
	def enabled(self):
		return self._c.enabled

class PaludisChoiceSet(SpaceSepFrozenSet):
	def __new__(self, choices):
		def _get_iuse():
			for group in choices:
				if group.raw_name == 'build_options': # paludis specific
					continue
				for c in group:
					if c.explicitly_listed:
						yield PaludisChoice(c)

		self._choices = choices
		return SpaceSepFrozenSet.__new__(self, _get_iuse())

	def __getitem__(self, k):
		try:
			return SpaceSepFrozenSet.__getitem__(self, k)
		except KeyError:
			for group in self._choices:
				for c in group:
					if str(c.name_with_prefix) == k:
						return PaludisChoice(c)
			raise

class PaludisID(PMPackage, PaludisAtom):
	def __init__(self, pkg, env):
		self._pkg = pkg
		self._env = env

	@property
	def metadata(self):
		return PaludisMetadata(self._pkg)

	@property
	def path(self):
		return self._pkg.fs_location_key().parse_value()

	@property
	def slotted_atom(self):
		cp = str(self.key)
		slot = self.slot
		return PaludisAtom('%s:%s' % (cp, slot), self._env)

	@property
	def unversioned_atom(self):
		return PaludisAtom(str(self.key), self._env)

	@property
	def key(self):
		return PaludisBoundPackageKey(self._pkg.name, self)

	@property
	def version(self):
		return PaludisPackageVersion(self._pkg.version)

	def _get_meta(self, key):
		if isinstance(key, str):
			key = self._pkg.find_metadata(key)
		if key is None:
			return ()
		return key.parse_value()

	@property
	def eapi(self):
		return str(self._get_meta('EAPI'))

	@property
	def description(self):
		return PaludisPackageDescription(self._pkg)

	@property
	def inherits(self):
		return SpaceSepFrozenSet(self._get_meta('INHERITED'))

	@property
	def defined_phases(self):
		ret = SpaceSepFrozenSet(self._get_meta('DEFINED_PHASES'))
		if not ret:
			return None
		elif ret == ('-',):
			return SpaceSepFrozenSet(())
		return ret

	@property
	def homepages(self):
		spec = self._get_meta(self._pkg.homepage_key())
		return SpaceSepTuple([str(x) for x in spec])

	@property
	def keywords(self):
		kws = self._get_meta(self._pkg.keywords_key())
		return SpaceSepFrozenSet([str(x) for x in kws])

	@property
	def slot(self):
		return str(self._get_meta(self._pkg.slot_key()))

	@property
	def repository(self):
		return str(self._pkg.repository_name)

	@property
	def build_dependencies(self):
		return PaludisPackageDepSet(
				self._get_meta(self._pkg.build_dependencies_key()),
				self)

	@property
	def run_dependencies(self):
		return PaludisPackageDepSet(
				self._get_meta(self._pkg.run_dependencies_key()),
				self)

	@property
	def post_dependencies(self):
		return PaludisPackageDepSet(
				self._get_meta(self._pkg.post_dependencies_key()),
				self)

	@property
	def required_use(self):
		k = self._pkg.find_metadata('REQUIRED_USE')
		if k is None:
			return None
		return PaludisPackageDepSet(
				self._get_meta('REQUIRED_USE'),
				self, PMRequiredUseAtom)

	@property
	def use(self):
		return PaludisChoiceSet(
				self._get_meta(self._pkg.choices_key()))

	@property
	def _atom(self):
		return self._pkg.uniquely_identifying_spec()

	def __str__(self):
		return str(self._atom)

	def __lt__(self, other):
		if not isinstance(other, PaludisID):
			raise TypeError('Unable to compare %s against %s' % \
					self, other)
		return self.key < other.key \
				or self.version < other.version \
				or self._env.more_important_than( \
						other.repository, self.repository)

class PaludisInstallableID(PaludisID, PMInstallablePackage):
	pass

class PaludisInstalledID(PaludisID, PMInstalledPackage):
	@property
	def contents(self):
		return PaludisPackageContents(
				self._get_meta(self._pkg.contents_key()))

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
