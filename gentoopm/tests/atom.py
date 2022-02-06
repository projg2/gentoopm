#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..exceptions import InvalidAtomStringError, AmbiguousPackageSetError

from . import PMTestCase, PackageNames


class UserSpecifiedAtomTestCase(PMTestCase):
    def setUp(self):
        self._incomplete_atom = self.pm.Atom(PackageNames.single)
        self._complete_atom = self.pm.Atom(PackageNames.single_complete)
        self._associated_atom = self.pm.stack.select(self._complete_atom)

    def test_invalid_atoms(self):
        self.assertRaises(InvalidAtomStringError, self.pm.Atom, "<>foo")
        self.assertRaises(InvalidAtomStringError, self.pm.Atom, "=bar")

    def test_incomplete_atom(self):
        a = self._incomplete_atom
        self.assertFalse(a.complete)

    def test_complete_atom(self):
        a = self._complete_atom
        self.assertTrue(a.complete)

    def test_atom_stringification(self):
        self.assertEqual("foo/bar", str(self.pm.Atom("foo/bar")))
        self.assertEqual(">=baz/bar-100", str(self.pm.Atom(">=baz/bar-100")))
        self.assertEqual("foo/baz:10", str(self.pm.Atom("foo/baz:10")))
        self.assertEqual("bar/baz::foo", str(self.pm.Atom("bar/baz::foo")))
        self.assertEqual(
            ">=foo/fooz-29.5:bazmania", str(self.pm.Atom(">=foo/fooz-29.5:bazmania"))
        )
        self.assertEqual(
            "~baz/inga-4.1:2::foo", str(self.pm.Atom("~baz/inga-4.1:2::foo"))
        )

    def test_atom_transformations(self):
        a = self._associated_atom
        cas = str(self._complete_atom)
        self.assertEqual(str(a.slotted_atom), "%s:0" % cas)
        self.assertEqual(str(a.unversioned_atom), cas)

    def test_atom_parts(self):
        a = self.pm.Atom(">=app-foo/bar-19-r1:5::baz")
        self.assertEqual(a.key.category, "app-foo")
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "app-foo/bar")
        self.assertEqual(a.version.without_revision, "19")
        self.assertEqual(a.version.revision, 1)
        self.assertEqual(a.version, "19-r1")
        self.assertEqual(a.slot, "5")
        self.assertEqual(a.repository, "baz")

    def test_atom_parts_incomplete(self):
        a = self.pm.Atom(">=bar-19-r1:5::baz")
        self.assertTrue(a.key.category is None)
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "bar")
        self.assertEqual(a.version.without_revision, "19")
        self.assertEqual(a.version.revision, 1)
        self.assertEqual(a.version, "19-r1")
        self.assertEqual(a.slot, "5")
        self.assertEqual(a.repository, "baz")

    def test_atom_parts_without_rev(self):
        a = self.pm.Atom(">=app-foo/bar-19:5::baz")
        self.assertEqual(a.key.category, "app-foo")
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "app-foo/bar")
        self.assertEqual(a.version.without_revision, "19")
        self.assertEqual(a.version.revision, 0)
        self.assertEqual(a.version, "19")
        self.assertEqual(a.slot, "5")
        self.assertEqual(a.repository, "baz")

    def test_atom_parts_without_version(self):
        a = self.pm.Atom("app-foo/bar:5::baz")
        self.assertEqual(a.key.category, "app-foo")
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "app-foo/bar")
        self.assertTrue(a.version is None)
        self.assertEqual(a.slot, "5")
        self.assertEqual(a.repository, "baz")

    def test_atom_parts_without_slot(self):
        a = self.pm.Atom("app-foo/bar::baz")
        self.assertEqual(a.key.category, "app-foo")
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "app-foo/bar")
        self.assertTrue(a.version is None)
        self.assertTrue(a.slot is None)
        self.assertEqual(a.repository, "baz")

    def test_atom_parts_unversioned(self):
        a = self.pm.Atom("app-foo/bar")
        self.assertEqual(a.key.category, "app-foo")
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "app-foo/bar")
        self.assertTrue(a.version is None)
        self.assertTrue(a.slot is None)
        self.assertTrue(a.repository is None)

    def test_atom_parts_dumb(self):
        a = self.pm.Atom("bar")
        self.assertTrue(a.key.category is None)
        self.assertEqual(a.key.package, "bar")
        self.assertEqual(a.key, "bar")
        self.assertTrue(a.version is None)
        self.assertTrue(a.slot is None)
        self.assertTrue(a.repository is None)

    def test_atom_slots(self):
        # Paludis does not allow dependency syntax on user-specified slots
        # FIXME: figure out how to test it better
        if self.pm.name != "paludis":
            a = self.pm.Atom("app-foo/bar:=")
            self.assertTrue(a.slot is None)
            self.assertTrue(a.subslot is None)
            self.assertEqual(a.slot_operator, "=")
            b = self.pm.Atom("app-foo/bar:*")
            self.assertTrue(b.slot is None)
            self.assertTrue(b.subslot is None)
            self.assertEqual(b.slot_operator, "*")
            c = self.pm.Atom("app-foo/bar:1=")
            self.assertEqual(c.slot, "1")
            self.assertTrue(c.subslot is None)
            self.assertEqual(c.slot_operator, "=")
        d = self.pm.Atom("app-foo/bar:1/2")
        self.assertEqual(d.slot, "1")
        self.assertEqual(d.subslot, "2")
        self.assertTrue(d.slot_operator is None)
        e = self.pm.Atom("app-foo/bar:1")
        self.assertEqual(e.slot, "1")
        self.assertTrue(e.subslot is None)
        self.assertTrue(e.slot_operator is None)

    def test_unqualified_atom_slots(self):
        # Paludis does not allow dependency syntax on user-specified slots
        # FIXME: figure out how to test it better
        if self.pm.name != "paludis":
            a = self.pm.Atom("bar:=")
            self.assertTrue(a.slot is None)
            self.assertTrue(a.subslot is None)
            self.assertEqual(a.slot_operator, "=")
            # FIXME: this is broken with recent pkgcore
            if self.pm.name != "pkgcore":
                b = self.pm.Atom("bar:*")
                self.assertTrue(b.slot is None)
                self.assertTrue(b.subslot is None)
                self.assertEqual(b.slot_operator, "*")
            c = self.pm.Atom("bar:1=")
            self.assertEqual(c.slot, "1")
            self.assertTrue(c.subslot is None)
            self.assertEqual(c.slot_operator, "=")
        d = self.pm.Atom("bar:1/2")
        self.assertEqual(d.slot, "1")
        self.assertEqual(d.subslot, "2")
        self.assertTrue(d.slot_operator is None)
        e = self.pm.Atom("bar:1")
        self.assertEqual(e.slot, "1")
        self.assertTrue(e.subslot is None)
        self.assertTrue(e.slot_operator is None)

    def tearDown(self):
        pass
