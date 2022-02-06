#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from . import PMTestCase, PackageNames


class RepositoriesTestCase(PMTestCase):
    def setUp(self):
        self._stack = self.pm.stack
        self._repo = self.pm.repositories[PackageNames.repository]

    def test_repo_iter(self):
        needle = PackageNames.repository
        for r in self.pm.repositories:
            if r.name == needle:
                break
        else:
            self.assertTrue(r.name == needle)

    def test_repo_contains(self):
        self.assertTrue(PackageNames.repository in self.pm.repositories)

    def test_repo_reverse_mapping(self):
        r = self._repo
        self.assertTrue(r.path in self.pm.repositories)
        self.assertEqual(r, self.pm.repositories[r.path])

    def test_stack_repos_equiv(self):
        patom = PackageNames.single_complete
        plist = set(self._stack.filter(patom))
        for r in self.pm.repositories:
            for p in r.filter(patom):
                self.assertTrue(p in plist)
                plist.remove(p)
        self.assertFalse(plist)  # empty

    def tearDown(self):
        pass
