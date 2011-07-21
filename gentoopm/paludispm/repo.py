#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractproperty

import paludis

from gentoopm.basepm.repo import PMRepository, PMRepositoryDict, \
		PMEbuildRepository
from gentoopm.paludispm.atom import PaludisAtom
from gentoopm.paludispm.pkg import PaludisInstallableID, PaludisInstalledID
from gentoopm.paludispm.pkgset import PaludisPackageSet

class PaludisRepoDict(PMRepositoryDict):
	def __iter__(self):
		for r in self._env.repositories:
			if r.format_key().parse_value() == 'e':
				yield PaludisLivefsRepository(r, self._env)

	def __init__(self, env):
		self._env = env

class PaludisEnumID(object):
	pass

class PaludisBaseRepo(PMRepository, PaludisPackageSet):
	def __init__(self, env):
		PaludisPackageSet.__init__(self, env, True)

	@property
	def _gen(self):
		return paludis.Generator.All()

	@property
	def _filt(self):
		return paludis.Filter.All()

	@abstractproperty
	def _pkg_class(self):
		pass

	def __iter__(self):
		enum = PaludisEnumID()
		for i, p in enumerate(self._env[paludis.Selection.AllVersionsSorted(
				paludis.FilteredGenerator(self._gen, self._filt))]):
			yield self._pkg_class(p, i, enum, self._env)

	def filter(self, *args, **kwargs):
		pset = self
		newargs = []

		for f in args:
			if isinstance(f, str):
				f = PaludisAtom(f, self._env)
			if isinstance(f, PaludisAtom):
				pset = PaludisAtomFilteredRepo(pset, f)
			else:
				newargs.append(f)

		if id(pset) == id(self):
			return PaludisPackageSet.filter(self, *args, **kwargs)
		elif newargs or kwargs:
			return pset.filter(*newargs, **kwargs)
		else:
			return pset

class PaludisAtomFilteredRepo(PaludisBaseRepo):
	@property
	def _gen(self):
		return self._mygen

	@property
	def _filt(self):
		return self._myfilt

	@property
	def _pkg_class(self):
		return self._mypkg_class

	def __init__(self, repo, atom):
		PaludisBaseRepo.__init__(self, repo._env)
		self._myfilt = repo._filt
		self._mygen = repo._gen & paludis.Generator.Matches(atom._atom,
				paludis.MatchPackageOptions())
		self._mypkg_class = repo._pkg_class

class PaludisStackRepo(PaludisBaseRepo):
	_pkg_class = PaludisInstallableID

	@property
	def _filt(self):
		return paludis.Filter.SupportsInstallAction()

class PaludisLivefsRepository(PaludisBaseRepo, PMEbuildRepository):
	_pkg_class = PaludisInstallableID

	def __init__(self, repo_obj, env):
		PaludisBaseRepo.__init__(self, env)
		self._repo = repo_obj

	@property
	def _gen(self):
		return paludis.Generator.InRepository(self._repo.name)

	@property
	def name(self):
		return str(self._repo.name)

	@property
	def path(self):
		return self._repo.location_key().parse_value()

class PaludisInstalledRepo(PaludisBaseRepo):
	_pkg_class = PaludisInstalledID

	@property
	def _filt(self):
		return paludis.Filter.InstalledAtRoot('/')
