#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011-2022 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pytest

from gentoopm.exceptions import AmbiguousPackageSetError, EmptyPackageSetError

from . import PackageNames


@pytest.fixture(scope="session", params=["installed", "stack", PackageNames.repository])
def repo(request, pm):
    if request.param in ["installed", "stack"]:
        return getattr(pm, request.param)
    return pm.repositories[request.param]


@pytest.fixture(scope="session", params=["stack", PackageNames.repository])
def installable_repo(request, pm):
    if request.param == "stack":
        return getattr(pm, request.param)
    return pm.repositories[request.param]


@pytest.fixture(
    scope="session", params=[PackageNames.single_complete, PackageNames.single]
)
def single_atom(request):
    return request.param


def test_atom_single_filter(repo, single_atom):
    assert any(repo.filter(single_atom))


def test_atom_single_select(repo, single_atom):
    assert repo.select(single_atom)


def test_atom_single_filter_bool(repo, single_atom):
    assert repo.filter(single_atom)


def test_atom_single_contains(repo, single_atom):
    assert single_atom in repo


def test_atom_single_getitem(installable_repo):
    with pytest.raises(AmbiguousPackageSetError):
        installable_repo[PackageNames.single_complete]


def test_atom_single_getitem_installed(pm):
    assert pm.installed[PackageNames.single_complete]


def test_atom_multiple_filter(installable_repo):
    assert len({p.key for p in installable_repo.filter(PackageNames.multiple)}) > 1


def test_atom_multiple_select(installable_repo):
    with pytest.raises(AmbiguousPackageSetError):
        list(installable_repo.select(PackageNames.multiple))


def test_atom_multiple_filter_bool(installable_repo):
    assert installable_repo.filter(PackageNames.multiple)


def test_atom_multiple_contains(installable_repo):
    assert PackageNames.multiple in installable_repo


def test_atom_empty_filter(repo):
    assert not any(repo.filter(PackageNames.empty))


def test_atom_empty_select(repo):
    with pytest.raises(EmptyPackageSetError):
        list(repo.select(PackageNames.empty))


def test_atom_empty_filter_bool(repo):
    assert not repo.filter(PackageNames.empty)


def test_atom_empty_contains(repo):
    assert not PackageNames.empty in repo


def test_getitem_atom_empty(repo):
    with pytest.raises(EmptyPackageSetError):
        repo[PackageNames.empty]
