#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pkgcore.restrictions.boolean as br

from .atom import PkgCoreAtom
from .pkg import PkgCorePackage


def transform_filters(args, kwargs):
    """
    Transform our filters into pkgcore restrictions whenever possible. Takes
    args and kwargs as passed to .filter() and returns a tuple (restriction,
    newargs, newkwargs).

    If no filters can be transformed, None is returned as restriction,
    and args & kwargs are returned unmodified.
    """

    newargs = []
    f = []

    for a in args:
        if isinstance(a, PkgCorePackage):
            a = str(a)
        if isinstance(a, str):
            a = PkgCoreAtom(a)
        if isinstance(a, PkgCoreAtom):
            f.append(a._r)
        else:
            newargs.append(a)

    if not f:
        f = None
    elif len(f) == 1:
        f = f[0]
    else:
        f = br.AndRestriction(*f)

    return (f, newargs, kwargs)
