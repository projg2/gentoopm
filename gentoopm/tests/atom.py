#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..exceptions import InvalidAtomStringError, AmbiguousPackageSetError

from . import PMTestCase, PackageNames

class UserSpecifiedAtomTestCase(PMTestCase):
	def setUp(self):
		self._incomplete_atom = self.pm.Atom(PackageNames.single)
		self._complete_atom = self.pm.Atom(PackageNames.single_complete)
		self._associated_atom = self._complete_atom.get_associated(self.pm.stack)

	def test_invalid_atoms(self):
		for atstr in ('<>foo', '=bar', '*/*::baz'):
			self.assertRaises(InvalidAtomStringError, self.pm.Atom, atstr)

	def test_incomplete_atom(self):
		a = self._incomplete_atom
		self.assertFalse(a.complete)
		self.assertFalse(a.associated)

	def test_complete_atom(self):
		a = self._complete_atom
		self.assertTrue(a.complete)
		self.assertFalse(a.associated)

	def test_atom_stringification(self):
		for atstr in ('foo/bar', '>=baz/bar-100', 'foo/baz:10',
				'bar/baz::foo', '>=foo/fooz-29.5:bazmania', '~baz/inga-4.1:2::foo'):
			self.assertEqual(atstr, str(self.pm.Atom(atstr)))

	def test_atom_association(self):
		a = self._associated_atom
		self.assertTrue(a.complete)
		self.assertTrue(a.associated)

	def test_incomplete_atom_association(self):
		a = self._incomplete_atom.get_associated(self.pm.stack)
		self.assertTrue(a.complete)
		self.assertTrue(a.associated)

	def test_ambiguous_atom_association(self):
		ia = self.pm.Atom(PackageNames.multiple)
		self.assertRaises(AmbiguousPackageSetError, ia.get_associated,
				self.pm.stack)

	def test_atom_transformations(self):
		a = self._associated_atom
		cas = str(self._complete_atom)
		self.assertEqual(str(a.slotted), '%s:0' % cas)
		self.assertEqual(str(a.unversioned), cas)

	def test_atom_parts(self):
		a = self.pm.Atom('>=app-foo/bar-19-r1:5::baz')
		self.assertEqual(a.key.category, 'app-foo')
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'app-foo/bar')
		self.assertEqual(a.version.without_revision, '19')
		self.assertEqual(a.version.revision, 1)
		self.assertEqual(a.version, '19-r1')
		self.assertEqual(a.slot, '5')
		self.assertEqual(a.repository, 'baz')

	def test_atom_parts_incomplete(self):
		a = self.pm.Atom('>=bar-19-r1:5::baz')
		self.assertTrue(a.key.category is None)
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'bar')
		self.assertEqual(a.version.without_revision, '19')
		self.assertEqual(a.version.revision, 1)
		self.assertEqual(a.version, '19-r1')
		self.assertEqual(a.slot, '5')
		self.assertEqual(a.repository, 'baz')

	def test_atom_parts_without_rev(self):
		a = self.pm.Atom('>=app-foo/bar-19:5::baz')
		self.assertEqual(a.key.category, 'app-foo')
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'app-foo/bar')
		self.assertEqual(a.version.without_revision, '19')
		self.assertEqual(a.version.revision, 0)
		self.assertEqual(a.version, '19')
		self.assertEqual(a.slot, '5')
		self.assertEqual(a.repository, 'baz')

	def test_atom_parts_without_version(self):
		a = self.pm.Atom('app-foo/bar:5::baz')
		self.assertEqual(a.key.category, 'app-foo')
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'app-foo/bar')
		self.assertTrue(a.version is None)
		self.assertEqual(a.slot, '5')
		self.assertEqual(a.repository, 'baz')

	def test_atom_parts_without_slot(self):
		a = self.pm.Atom('app-foo/bar::baz')
		self.assertEqual(a.key.category, 'app-foo')
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'app-foo/bar')
		self.assertTrue(a.version is None)
		self.assertTrue(a.slot is None)
		self.assertEqual(a.repository, 'baz')

	def test_atom_parts_unversioned(self):
		a = self.pm.Atom('app-foo/bar')
		self.assertEqual(a.key.category, 'app-foo')
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'app-foo/bar')
		self.assertTrue(a.version is None)
		self.assertTrue(a.slot is None)
		self.assertTrue(a.repository is None)

	def test_atom_parts_dumb(self):
		a = self.pm.Atom('bar')
		self.assertTrue(a.key.category is None)
		self.assertEqual(a.key.package, 'bar')
		self.assertEqual(a.key, 'bar')
		self.assertTrue(a.version is None)
		self.assertTrue(a.slot is None)
		self.assertTrue(a.repository is None)

	def tearDown(self):
		pass
