#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from collections import namedtuple
from portage.dep import paren_reduce, use_reduce

from ..basepm.depend import (
    PMPackageDepSet,
    PMConditionalDep,
    PMAnyOfDep,
    PMAllOfDep,
    PMExactlyOneOfDep,
    PMAtMostOneOfDep,
    PMBaseDep,
)


class PortageBaseDep(PMBaseDep):
    def __init__(self, deps, args):
        self._deps = deps
        self._args = args

    def __iter__(self):
        it = iter(self._deps)
        for d in it:
            if isinstance(d, list):
                yield PortageAllOfDep(it, self._args)
            elif d == "||":
                yield PortageAnyOfDep(next(it), self._args)
            elif d == "&&":
                yield PortageAllOfDep(next(it), self._args)
            elif d == "??":
                yield PortageAtMostOneOfDep(next(it), self._args)
            elif d == "__xor__?":
                yield PortageExactlyOneOfDep(next(it), self._args)
            elif d.endswith("?"):
                yield PortageConditionalUseDep(next(it), self._args, d.rstrip("?"))
            else:
                yield self._args.cls(d)


class PortageAnyOfDep(PMAnyOfDep, PortageBaseDep):
    pass


class PortageAllOfDep(PMAllOfDep, PortageBaseDep):
    pass


class PortageExactlyOneOfDep(PMExactlyOneOfDep, PortageBaseDep):
    pass


class PortageAtMostOneOfDep(PMAtMostOneOfDep, PortageBaseDep):
    pass


class PortageConditionalUseDep(PMConditionalDep, PortageBaseDep):
    def __init__(self, deps, args, flag):
        PortageBaseDep.__init__(self, deps, args)
        self._flag = flag

    @property
    def enabled(self):
        return self._flag in self._args.puse


_argtuple = namedtuple("PortageDepArgTuple", ("puse", "cls"))


class PortagePackageDepSet(PMPackageDepSet, PortageBaseDep):
    def __init__(self, s, *args):
        self._use_reducable = not "^^" in s
        # ARGV, paren_reduce() doesn't handle ^^
        # so we hack it to a __xor__?, UGLY!
        self._depstr = s.replace("^^", "__xor__?")
        PortageBaseDep.__init__(self, None, _argtuple(*args))

    def __iter__(self):
        if self._deps is None:
            self._deps = paren_reduce(self._depstr)
        return PortageBaseDep.__iter__(self)

    @property
    def without_conditionals(self):
        if self._use_reducable:
            return PortageUncondAllOfDep(
                use_reduce(self._depstr, self._args.puse), self._args
            )
        return PMPackageDepSet.without_conditionals.fget(self)


class PortageUncondDep(PortageBaseDep):
    @property
    def without_conditionals(self):
        return self

    def __iter__(self):
        it = iter(self._deps)
        for d in it:
            if d == "||":
                yield PortageUncondAnyOfDep(next(it), self._args)
            elif d == "&&":
                yield PortageUncondAllOfDep(next(it), self._args)
            elif d == "??":
                yield PortageUncondAtMostOneOfDep(next(it), self._args)
            elif d == "__xor__?":
                yield PortageUncondExactlyOneOfDep(next(it), self._args)
            else:
                yield self._args.cls(d)


class PortageUncondAnyOfDep(PMAnyOfDep, PortageUncondDep):
    pass


class PortageUncondAllOfDep(PMAllOfDep, PortageUncondDep):
    pass


class PortageUncondExactlyOneOfDep(PMExactlyOneOfDep, PortageUncondDep):
    pass


class PortageUncondAtMostOneOfDep(PMAtMostOneOfDep, PortageUncondDep):
    pass
