#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from . import PMTestCase, PackageNames

class PackagesTestCase(PMTestCase):
	def setUp(self):
		self._inst_pkg = self.pm.installed.select(PackageNames.single_complete)
		self._stack_pkg = self.pm.stack.select(PackageNames.single_complete)
		self._pkgs = (self._inst_pkg, self._stack_pkg)

	def test_key_id(self):
		""" Check whether package IDs are unique and keys are not. """
		for r in (self.pm.installed, self.pm.stack):
			ids = set()
			key = None
			for p in r.filter(PackageNames.single_complete):
				self.assertFalse(p.id in ids)
				ids.add(p.id)
				if key is not None:
					self.assertEqual(p.key, key)
				else:
					key = p.key

	def test_key_state(self):
		""" Check whether package keys set state correctly. """
		self.assertTrue(self._inst_pkg.key.state.installed)
		self.assertTrue(self._stack_pkg.key.state.installable)
		self.assertNotEqual(self._inst_pkg.key, self._stack_pkg.key)

	def test_path_exists(self):
		""" Check whether the path returned is ok (if any). """
		for p in self._pkgs:
			if p.path:
				self.assertTrue(os.path.exists(p.path))

	def test_atom_reverse(self):
		""" Check whether the atom matches the same package. """
		for r in (self.pm.installed, self.pm.stack):
			# get worst match
			p = next(iter(sorted(r.filter(PackageNames.single_complete))))

			self.assertEqual(p, r[p.atom])
			self.assertEqual(p.key, r.select(p.atom.slotted).key)
			self.assertEqual(p.key, r.select(p.atom.unversioned).key)

	def test_metadata_inherited(self):
		""" Check the INHERITED metadata var. It was known to cause problems
			with pkgcore. """
		for p in self._pkgs:
			p.metadata['INHERITED']

	def test_metadata_dict_attr(self):
		""" Check whether metadata is accessible with dict & attrs. """
		mks = ('EAPI', 'INHERITED', 'DESCRIPTION')
		for p in self._pkgs:
			for k in mks:
				self.assertEqual(p.metadata[k], getattr(p.metadata, k))

	def test_metadata_invalid(self):
		""" Check whether invalid metadata access raises an exception. """
		rk = 'FOOBAR'
		for p in self._pkgs:
			self.assertFalse(rk in p.metadata)
			self.assertRaises(KeyError, lambda m, rk: m[rk], p.metadata, rk)
			self.assertRaises(AttributeError, getattr, p.metadata, rk)

	def test_description(self):
		""" Check whether description works as expected. """
		for p in self._pkgs:
			self.assertEqual(str(p.description),
					p.description.long if p.description.long is not None
					else p.description.short)

	def test_inherits(self):
		""" Check whether inherits are an iterable of stringifiables. """
		for p in self._pkgs:
			if p.inherits is not None:
				try:
					self.assertTrue(str(next(iter(p.inherits))))
				except StopIteration:
					pass

	def test_environ_dict(self):
		""" Try to access environment.bz2 via dict. """
		rk = PackageNames.envsafe_metadata_key
		for p in (self._inst_pkg,):
			self.assertEqual(p.metadata[rk], p.environ[rk])

	def test_environ_copy(self):
		""" Try to access environment.bz2 via .copy(). """
		rk = PackageNames.envsafe_metadata_key
		for p in (self._inst_pkg,):
			self.assertEqual(p.metadata[rk], p.environ.copy(rk)[rk])

	def test_environ_fork(self):
		""" Test forking environment accessor. """
		rk = PackageNames.envsafe_metadata_key
		for p in (self._inst_pkg,):
			forkenv = p.environ.fork()
			self.assertEqual(p.metadata[rk], forkenv[rk])
			del forkenv

	def test_contents(self):
		""" Test .contents. """
		p = self._inst_pkg
		f = next(iter(p.contents))
		self.assertTrue(f in p.contents)

	def tearDown(self):
		pass
