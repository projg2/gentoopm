#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis, re
from collections import namedtuple

from ..basepm.depend import (
    PMPackageDepSet,
    PMConditionalDep,
    PMAnyOfDep,
    PMAllOfDep,
    PMExactlyOneOfDep,
    PMAtMostOneOfDep,
    PMBaseDep,
)

from .atom import PaludisAtom

_block_re = re.compile("^!*")


class PaludisBaseDep(PMBaseDep):
    def __init__(self, deps, args):
        self._deps = deps
        self._args = args

    def __iter__(self):
        for d in self._deps:
            if isinstance(d, paludis.PackageDepSpec):
                assert self._args.cls is None
                yield PaludisAtom(d, self._args.env)
            elif isinstance(d, paludis.BlockDepSpec):
                assert self._args.cls is None
                yield PaludisAtom(
                    d.blocking, self._args.env, block=_block_re.match(d.text).group(0)
                )
            elif isinstance(d, paludis.AnyDepSpec):
                yield PaludisAnyOfDep(d, self._args)
            elif isinstance(d, paludis.AllDepSpec):
                yield PaludisAllOfDep(d, self._args)
            elif isinstance(d, paludis.ExactlyOneDepSpec):
                yield PaludisExactlyOneOfDep(d, self._args)
            elif isinstance(d, paludis.AtMostOneDepSpec):
                yield PaludisAtMostOneOfDep(d, self._args)
            elif isinstance(d, paludis.ConditionalDepSpec):
                yield PaludisConditionalDep(d, self._args)
            elif isinstance(d, paludis.PlainTextDepSpec):
                assert self._args.cls is not None
                yield self._args.cls(str(d))
            else:
                raise NotImplementedError("Unable to parse %s" % repr(d))


class PaludisAnyOfDep(PMAnyOfDep, PaludisBaseDep):
    pass


class PaludisAllOfDep(PMAllOfDep, PaludisBaseDep):
    pass


class PaludisExactlyOneOfDep(PMExactlyOneOfDep, PaludisBaseDep):
    pass


class PaludisAtMostOneOfDep(PMAtMostOneOfDep, PaludisBaseDep):
    pass


class PaludisConditionalDep(PMConditionalDep, PaludisBaseDep):
    @property
    def enabled(self):
        return self._deps.condition_met(self._args.env, self._args.pkg)


_argtuple = namedtuple("PaludisDepArgTuple", ("env", "pkg", "cls"))


class PaludisPackageDepSet(PMPackageDepSet, PaludisAllOfDep):
    def __init__(self, deps, pkg, cls=None):
        PaludisAllOfDep.__init__(self, deps, _argtuple(pkg._env, pkg._pkg, cls))
