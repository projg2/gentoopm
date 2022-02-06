#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from ..exceptions import AmbiguousPackageSetError, EmptyPackageSetError
from ..util import BoolCompat

from . import PMTestCase, PackageNames


class IterChecker(BoolCompat):
    def __init__(self, iterable):
        self._it = iter(iterable)

    def __bool__(self):
        try:
            next(self._it)
        except StopIteration:
            return False
        else:
            return True


class PackageSetsTestCase(PMTestCase):
    def setUp(self):
        self._inst = self.pm.installed
        self._stack = self.pm.stack
        self._repo = self.pm.repositories[PackageNames.repository]
        self._repos = (self._inst, self._stack, self._repo)

    def test_filter_atom(self):
        at = PackageNames.single_complete
        for r in self._repos:
            self.assertTrue(IterChecker(r.filter(at)))

    def test_filter_atom_incomplete(self):
        at = PackageNames.single
        for r in self._repos:
            self.assertTrue(IterChecker(r.filter(at)))

    def test_filter_atom_multiple(self):
        """Check whether multi-matching atoms return multiple packages."""
        at = PackageNames.multiple
        for r in (self._repo, self._stack):
            keys = set()
            for p in r.filter(at):
                keys.add(p.key)
            self.assertTrue(len(keys) > 1)

    def test_filter_atom_empty(self):
        at = PackageNames.empty
        for r in self._repos:
            self.assertFalse(IterChecker(r.filter(at)))

    def test_select_atom(self):
        at = PackageNames.single_complete
        for r in self._repos:
            self.assertTrue(r.select(at))

    def test_select_atom_incomplete(self):
        at = PackageNames.single
        for r in self._repos:
            self.assertTrue(r.select(at))

    def test_select_atom_multiple(self):
        at = PackageNames.multiple
        for r in (self._repo, self._stack):
            self.assertRaises(AmbiguousPackageSetError, r.select, at)

    def test_select_atom_empty(self):
        at = PackageNames.empty
        for r in self._repos:
            self.assertRaises(EmptyPackageSetError, r.select, at)

    def test_getitem_atom(self):
        at = PackageNames.single_complete
        for r in (self._stack, self._repo):
            self.assertRaises(AmbiguousPackageSetError, lambda r, at: r[at], r, at)
        self.assertTrue(self._inst[at])

    def test_getitem_atom_empty(self):
        at = PackageNames.empty
        for r in self._repos:
            self.assertRaises(EmptyPackageSetError, lambda r, at: r[at], r, at)

    def test_nonzero_true(self):
        at = PackageNames.single_complete
        for r in self._repos:
            pset = r.filter(at)
            self.assertTrue(IterChecker(pset))
            self.assertTrue(pset)

    def test_nonzero_false(self):
        at = PackageNames.empty
        for r in self._repos:
            pset = r.filter(at)
            self.assertFalse(IterChecker(pset))
            self.assertFalse(pset)

    def test_contains_atom(self):
        at = PackageNames.single_complete
        for r in self._repos:
            self.assertTrue(at in r)

    def test_contains_atom_multiple(self):
        at = PackageNames.multiple
        for r in (self._repo, self._stack):
            self.assertTrue(at in r)

    def test_contains_atom_empty(self):
        at = PackageNames.empty
        for r in self._repos:
            self.assertFalse(at in r)

    def tearDown(self):
        pass
