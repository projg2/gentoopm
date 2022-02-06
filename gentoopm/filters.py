#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from operator import attrgetter

from .basepm.filter import PMPackageMatcher


class AttributeMatch(PMPackageMatcher):
    """
    A filter matching package attributes with values.
    """

    def __init__(self, key, val):
        self._getter = attrgetter(key)
        self._val = val

    def __call__(self, pkg):
        return self._val == self._getter(pkg)
