# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

from . import PackageNames


def test_repo_iter(pm):
    assert any(r.name == PackageNames.repository for r in pm.repositories)


def test_repo_contains(pm):
    assert PackageNames.repository in pm.repositories


def test_repo_reverse_mapping(pm):
    repo = pm.repositories[PackageNames.repository]
    assert repo.path in pm.repositories
    assert repo == pm.repositories[repo.path]


def test_stack_repos_equiv(pm):
    patom = PackageNames.single_complete
    stack_plist = set(pm.stack.filter(patom))
    repo_plist = set(pkg for repo in pm.repositories for pkg in repo.filter(patom))
    assert stack_plist == repo_plist
