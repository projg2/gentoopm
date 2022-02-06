#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import unittest


class PMTestCase(unittest.TestCase):
    _pm = None

    @property
    def pm(self):
        if self._pm is None:
            from gentoopm import get_package_manager

            self._pm = get_package_manager()
        return self._pm


class PackageNames(object):
    """
    A container for package names used in tests. Supposed to allow simple
    switch to another packages when one of them stops to work.
    """

    single = "single"
    """ Incomplete atom matching a single package. """

    single_complete = "a/single"
    """ Complete atom matching a single package. """

    single_use = "example-flag"
    """ A USEflag which should be available on the package above. """

    multiple = "multi"
    """ Incomplete atom matching multiple packages. """

    empty = "a/nonexist"
    """ Atom matching no packages. """

    subslotted = "a/subslotted"
    """ Atom matching a subslotted package. """

    pmasked = "=a/pmasked-2"
    """ Atom matching a p.masked package. """

    nonpmasked = "=a/pmasked-1"
    """ Atom matching a non-p.masked package. """

    repository = "gentoo"
    """ Repository name guaranteed to match. """

    envsafe_metadata_key = "DESCRIPTION"
    """ Metadata key which should be safe to match with environment.bz2. """

    @staticmethod
    def envsafe_metadata_acc(pkg):
        """Package metadata accessor matching the L{envsafe_metadata_key}."""
        return pkg.description.short
