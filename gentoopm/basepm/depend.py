#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from ..util import ABCObject, StringCompat


class PMRequiredUseAtom(StringCompat):
    """
    An atom for C{REQUIRED_USE} specification.
    """

    def __init__(self, s):
        self._blocks = s.startswith("!")
        if self._blocks:
            s = s[1:]
        self._flag = s

    @property
    def name(self):
        """
        Relevant USE flag name.

        @type: string
        """
        return self._flag

    @property
    def blocking(self):
        """
        Whether the atom blocks the USE flag (requires it not to be set).

        @type: bool
        """
        return self._blocks

    @property
    def requiring(self):
        """
        Whether the atom requires the USE flag to be set.

        @type: bool
        """
        return not self._blocks


class PMBaseDep(ABCObject):
    """
    Base class for a dependency list holder.
    """

    @abstractmethod
    def __iter__(self):
        """
        Iterate over dependency items.

        @rtype: iter(L{PMBaseDep},L{PMAtom})
        """
        pass

    @abstractproperty
    def without_conditionals(self):
        """
        Return the depspec with all conditionals resolved.

        @type: L{PMUncondAllOfDep}
        """
        pass

    def __repr__(self):
        l = ["\n".join(["\t%s" % x for x in repr(d).splitlines()]) for d in self]
        return "%s(\n%s)" % (self.__class__.__name__, ",\n".join(l))


class PMUncondBaseDep(PMBaseDep):
    def __init__(self, parent):
        self._parent = parent

    @property
    def without_conditionals(self):
        return self

    def _iter_deps(self, deps):
        for d in deps:
            if isinstance(d, PMConditionalDep):
                if d.enabled:
                    for d in self._iter_deps(d):
                        yield d
            elif isinstance(d, PMAnyOfDep):
                yield PMUncondAnyOfDep(d)
            else:
                yield d

    def __iter__(self):
        return self._iter_deps(self._parent)


class PMConditionalDep(PMBaseDep):
    """
    A conditional dependency set (enabled by a condition of some kind).
    """

    @property
    def without_conditionals(self):
        return PMUncondAllOfDep((self,))

    @abstractproperty
    def enabled(self):
        """
        Whether the dependency set is enabled (the condition is met).

        @type: bool
        """
        pass


class PMAllOfDep(PMBaseDep):
    """
    An all-of dependency block (C{( ... ... )}).
    """

    @property
    def without_conditionals(self):
        return PMUncondAllOfDep(self)


class PMUncondAllOfDep(PMAllOfDep, PMUncondBaseDep):
    pass


class PMAnyOfDep(PMBaseDep):
    """
    A one-of dependency set (C{|| ( ... )}).
    """

    @property
    def without_conditionals(self):
        return PMUncondAnyOfDep(self)


class PMUncondAnyOfDep(PMAnyOfDep, PMUncondBaseDep):
    pass


class PMExactlyOneOfDep(PMBaseDep):
    """
    An exactly-one-of (xor) dependency set (C{^^ ( ... )}).
    """

    @property
    def without_conditionals(self):
        return PMUncondExactlyOneOfDep(self)


class PMUncondExactlyOneOfDep(PMExactlyOneOfDep, PMUncondBaseDep):
    pass


class PMAtMostOneOfDep(PMBaseDep):
    """
    An at-most-one-of dependency set (C{?? ( ... )}).
    """

    @property
    def without_conditionals(self):
        return PMUncondAtMostOneOfDep(self)


class PMUncondAtMostOneOfDep(PMAtMostOneOfDep, PMUncondBaseDep):
    pass


class PMPackageDepSet(PMAllOfDep):
    """
    A base class representing a depset (or depset-like variable) of a single
    package.
    """

    @property
    def without_conditionals(self):
        return PMUncondAllOfDep(self)
