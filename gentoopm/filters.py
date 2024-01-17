# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

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
