#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path

from . import PMTestCase, PackageNames


class PackagesTestCase(PMTestCase):
    def setUp(self):
        self._inst_pkg = self.pm.installed.select(PackageNames.single_complete)
        self._stack_pkg = self.pm.stack.select(PackageNames.single_complete)
        self._subslotted_pkg = self.pm.stack.select(PackageNames.subslotted)
        self._pmasked_pkg = self.pm.stack.select(PackageNames.pmasked)
        self._nonpmasked_pkg = self.pm.stack.select(PackageNames.nonpmasked)
        self._pkgs = (self._inst_pkg, self._stack_pkg)

    def test_key_id(self):
        """Check whether package IDs are unique and keys are not."""
        for r in (self.pm.installed, self.pm.stack):
            ids = set()
            key = None
            for p in r.filter(PackageNames.single_complete):
                self.assertFalse(p in ids)
                ids.add(p)
                if key is not None:
                    self.assertEqual(p.key, key)
                else:
                    key = p.key

    def test_key_state(self):
        """Check whether package keys set state correctly."""
        self.assertTrue(self._inst_pkg.key.state.installed)
        self.assertTrue(self._stack_pkg.key.state.installable)
        self.assertNotEqual(self._inst_pkg.key, self._stack_pkg.key)

    def test_path_exists(self):
        """Check whether the path returned is ok (if any)."""
        for p in self._pkgs:
            if p.path:
                self.assertTrue(os.path.exists(p.path))

    def test_atom_reverse(self):
        """Check whether the atom matches the same package."""
        for r in (self.pm.installed, self.pm.stack):
            # get worst match
            p = next(iter(sorted(r.filter(PackageNames.single_complete))))

            self.assertEqual(p, r[p])
            self.assertEqual(p.key, r.select(p.slotted_atom).key)
            self.assertEqual(p.key, r.select(p.unversioned_atom).key)

    def test_metadata_inherited(self):
        """Check the INHERITED metadata var. It was known to cause problems
        with pkgcore."""
        for p in self._pkgs:
            p.inherits

    def test_inherits(self):
        """Check whether inherits are an iterable of stringifiables."""
        for p in self._pkgs:
            if p.inherits is not None:
                try:
                    self.assertTrue(str(next(iter(p.inherits))))
                except StopIteration:
                    pass

    def test_environ_dict(self):
        """Try to access environment.bz2 via dict."""
        rk = PackageNames.envsafe_metadata_key
        ra = PackageNames.envsafe_metadata_acc
        for p in (self._inst_pkg,):
            self.assertEqual(ra(p), p.environ[rk])

    def test_environ_copy(self):
        """Try to access environment.bz2 via .copy()."""
        rk = PackageNames.envsafe_metadata_key
        ra = PackageNames.envsafe_metadata_acc
        for p in (self._inst_pkg,):
            self.assertEqual(ra(p), p.environ.copy(rk)[rk])

    def test_environ_fork(self):
        """Test forking environment accessor."""
        rk = PackageNames.envsafe_metadata_key
        ra = PackageNames.envsafe_metadata_acc
        for p in (self._inst_pkg,):
            forkenv = p.environ.fork()
            self.assertEqual(ra(p), forkenv[rk])
            del forkenv

    def test_contents(self):
        """Test .contents."""
        p = self._inst_pkg
        f = next(iter(p.contents))
        self.assertTrue(f in p.contents)

    def test_use(self):
        """Test .use."""
        p = self._inst_pkg
        fl = PackageNames.single_use
        self.assertTrue(fl in p.use)

    def test_slot(self):
        """Test .slot and friends."""
        p = self._subslotted_pkg
        # ensure that subslot is not included in slot nor slotted atom
        self.assertTrue("/" not in p.slot)
        self.assertTrue("/" not in str(p.slotted_atom).split(":")[1])
        # ensure that subslot is not null
        self.assertTrue(p.subslot)

    def test_non_subslotted(self):
        """Test .subslot on package not using explicit subslots."""
        p = self._stack_pkg
        self.assertEqual(p.slot, p.subslot)

    def test_maintainers(self):
        """Test .maintainers on a package having them."""
        p = self._stack_pkg
        # TODO: remove this hack once portage&paludis give us maintainers
        if p.maintainers is None:
            self.skipTest("Maintainers not implemented?")
        m_emails = [m.email for m in p.maintainers]
        self.assertTrue(len(m_emails) == 2)
        self.assertTrue("test@example.com" in m_emails)
        self.assertTrue("test2@example.com" in m_emails)

    def test_no_maintainers(self):
        """Test .maintainres on a package not having them."""
        p = self._subslotted_pkg
        # TODO: remove this hack once portage&paludis give us maintainers
        if p.maintainers is None:
            self.skipTest("Maintainers not implemented?")
        self.assertTrue(len(p.maintainers) == 0)

    def test_repo_masked(self):
        p = self._pmasked_pkg
        try:
            self.assertTrue(p.repo_masked)
        except NotImplementedError:
            self.skipTest("repo_masked not implemented")

    def test_nonrepo_masked(self):
        p = self._nonpmasked_pkg
        try:
            self.assertFalse(p.repo_masked)
        except NotImplementedError:
            self.skipTest("repo_masked not implemented")

    def tearDown(self):
        pass
