#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011-2023 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pytest

from gentoopm.exceptions import InvalidAtomStringError

from . import PackageNames


@pytest.mark.parametrize("atom", ["<>foo-11", "=bar"])
def test_invalid_atoms(pm, atom):
    with pytest.raises(InvalidAtomStringError):
        pm.Atom(atom)


def test_incomplete_atom(pm):
    assert not pm.Atom(PackageNames.single).complete


def test_complete_atom(pm):
    assert pm.Atom(PackageNames.single_complete).complete


@pytest.mark.parametrize(
    "atom",
    [
        "foo/bar",
        ">=baz/bar-100",
        "foo/baz:10",
        "bar/baz::foo",
        ">=foo/fooz-29.5:bazmania",
        "~baz/inga-4.1:2::foo",
    ],
)
def test_atom_str(pm, atom):
    assert str(pm.Atom(atom)) == atom


def test_atom_transformations(pm):
    atom = pm.Atom(PackageNames.single_complete)
    pkg = pm.stack.select(atom)
    cas = str(atom)
    assert str(pkg.slotted_atom) == f"{cas}:0"
    assert str(pkg.unversioned_atom) == cas


def test_atom_parts(pm):
    atom = pm.Atom(">=app-foo/bar-19-r1:5::baz")
    assert atom.key.category == "app-foo"
    assert atom.key.package == "bar"
    assert atom.key == "app-foo/bar"
    assert atom.version.without_revision == "19"
    assert atom.version.revision == 1
    assert atom.version == "19-r1"
    assert atom.slot == "5"
    assert atom.repository == "baz"


def test_atom_parts_incomplete(pm):
    atom = pm.Atom(">=bar-19-r1:5::baz")
    assert atom.key.category is None
    assert atom.key.package == "bar"
    assert atom.key == "bar"
    assert atom.version.without_revision == "19"
    assert atom.version.revision == 1
    assert atom.version == "19-r1"
    assert atom.slot == "5"
    assert atom.repository == "baz"


def test_atom_parts_without_rev(pm):
    atom = pm.Atom(">=app-foo/bar-19:5::baz")
    assert atom.key.category == "app-foo"
    assert atom.key.package == "bar"
    assert atom.key == "app-foo/bar"
    assert atom.version.without_revision == "19"
    assert atom.version.revision == 0
    assert atom.version == "19"
    assert atom.slot == "5"
    assert atom.repository == "baz"


def test_atom_parts_without_version(pm):
    atom = pm.Atom("app-foo/bar:5::baz")
    assert atom.key.category == "app-foo"
    assert atom.key.package == "bar"
    assert atom.key == "app-foo/bar"
    assert atom.version is None
    assert atom.slot == "5"
    assert atom.repository == "baz"


def test_atom_parts_without_slot(pm):
    atom = pm.Atom("app-foo/bar::baz")
    assert atom.key.category == "app-foo"
    assert atom.key.package == "bar"
    assert atom.key == "app-foo/bar"
    assert atom.version is None
    assert atom.slot is None
    assert atom.repository == "baz"


def test_atom_parts_unversioned(pm):
    atom = pm.Atom("app-foo/bar")
    assert atom.key.category == "app-foo"
    assert atom.key.package == "bar"
    assert atom.key == "app-foo/bar"
    assert atom.version is None
    assert atom.slot is None
    assert atom.repository is None


def test_atom_parts_dumb(pm):
    atom = pm.Atom("bar")
    assert atom.key.category is None
    assert atom.key.package == "bar"
    assert atom.key == "bar"
    assert atom.version is None
    assert atom.slot is None
    assert atom.repository is None


def test_atom_slots(pm):
    a = pm.Atom("app-foo/bar:=")
    assert a.slot is None
    assert a.subslot is None
    assert a.slot_operator == "="
    b = pm.Atom("app-foo/bar:*")
    assert b.slot is None
    assert b.subslot is None
    assert b.slot_operator == "*"
    c = pm.Atom("app-foo/bar:1=")
    assert c.slot == "1"
    assert c.subslot is None
    assert c.slot_operator == "="
    d = pm.Atom("app-foo/bar:1/2")
    assert d.slot == "1"
    assert d.subslot == "2"
    assert d.slot_operator is None
    e = pm.Atom("app-foo/bar:1")
    assert e.slot == "1"
    assert e.subslot is None
    assert e.slot_operator is None


def test_unqualified_atom_slots(pm):
    a = pm.Atom("bar:=")
    assert a.slot is None
    assert a.subslot is None
    assert a.slot_operator == "="
    # FIXME: this is broken with recent pkgcore
    if pm.name != "pkgcore":
        b = pm.Atom("bar:*")
        assert b.slot is None
        assert b.subslot is None
        assert b.slot_operator == "*"
    c = pm.Atom("bar:1=")
    assert c.slot == "1"
    assert c.subslot is None
    assert c.slot_operator == "="
    d = pm.Atom("bar:1/2")
    assert d.slot == "1"
    assert d.subslot == "2"
    assert d.slot_operator is None
    e = pm.Atom("bar:1")
    assert e.slot == "1"
    assert e.subslot is None
    assert e.slot_operator is None
