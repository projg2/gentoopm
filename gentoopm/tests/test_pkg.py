#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011-2023 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pytest

import os.path

from . import PackageNames


@pytest.fixture(scope="session", params=["installed", "stack"])
def repo(request, pm):
    return getattr(pm, request.param)


@pytest.fixture(scope="session")
def inst_pkg(pm):
    return pm.installed.select(PackageNames.single_complete)


@pytest.fixture(scope="session")
def stack_pkg(pm):
    return pm.stack.select(PackageNames.single_complete)


@pytest.fixture(scope="session")
def subslotted_pkg(pm):
    return pm.stack.select(PackageNames.subslotted)


@pytest.fixture(scope="session")
def pkg(request, repo):
    return repo.select(PackageNames.single_complete)


def test_key_id(repo):
    """Test that IDs are unique while keys are not"""
    pkgs = list(repo.filter(PackageNames.single_complete))
    assert len(set(pkgs)) == len(pkgs)
    assert len(set(p.key for p in pkgs)) == 1


def test_key_state(inst_pkg, stack_pkg):
    assert inst_pkg.key.state.installed
    assert not inst_pkg.key.state.installable
    assert not stack_pkg.key.state.installed
    assert stack_pkg.key.state.installable
    assert inst_pkg.key != stack_pkg.key


def test_path_exists(pkg):
    if pkg.path is None:
        pytest.skip("no path")
    assert os.path.exists(pkg.path)


def test_atom_reverse(repo):
    # get the worst match
    pkg = sorted(repo.filter(PackageNames.single_complete))[0]
    assert repo[pkg] == pkg
    assert repo.select(pkg.slotted_atom).key == pkg.key
    assert repo.select(pkg.unversioned_atom).key == pkg.key


def test_inherited(pkg):
    if pkg.inherits is None:
        pytest.skip("inherits not supported")
    assert all(str(i) for i in pkg.inherits)


def test_environ_dict(inst_pkg):
    assert inst_pkg.environ[
        PackageNames.envsafe_metadata_key
    ] == PackageNames.envsafe_metadata_acc(inst_pkg)


def test_environ_copy(inst_pkg):
    assert inst_pkg.environ.copy(PackageNames.envsafe_metadata_key)[
        PackageNames.envsafe_metadata_key
    ] == PackageNames.envsafe_metadata_acc(inst_pkg)


def test_environ_fork(inst_pkg):
    forkenv = inst_pkg.environ.fork()
    assert forkenv[
        PackageNames.envsafe_metadata_key
    ] == PackageNames.envsafe_metadata_acc(inst_pkg)
    del forkenv


def test_contents(inst_pkg):
    assert all(f in inst_pkg.contents for f in inst_pkg.contents)


def test_use(inst_pkg):
    assert PackageNames.single_use in inst_pkg.use


def test_slot(subslotted_pkg):
    # ensure that subslot is not included in slot nor slotted atom
    assert "/" not in subslotted_pkg.slot
    assert "/" not in str(subslotted_pkg.slotted_atom).split(":")[1]
    # ensure that subslot is not null
    assert subslotted_pkg.subslot


def test_non_subslotted(stack_pkg):
    assert stack_pkg.slot == stack_pkg.subslot


def test_maintainers(stack_pkg):
    # TODO: remove this hack once portage give us maintainers
    if stack_pkg.maintainers is None:
        pytest.skip("maintainers not supported")
    assert [m.email for m in stack_pkg.maintainers] == [
        "test@example.com",
        "test2@example.com",
    ]


def test_no_maintainers(subslotted_pkg):
    # TODO: remove this hack once portage give us maintainers
    if subslotted_pkg.maintainers is None:
        pytest.skip("maintainers not supported")
    assert list(subslotted_pkg.maintainers) == []


def test_repo_masked(pm):
    pkg = pm.stack.select(PackageNames.pmasked)
    try:
        assert pkg.repo_masked
    except NotImplementedError:
        pytest.skip("repo_masked not implemented")


def test_non_repo_masked(pm):
    pkg = pm.stack.select(PackageNames.nonpmasked)
    try:
        assert not pkg.repo_masked
    except NotImplementedError:
        pytest.skip("repo_masked not implemented")
