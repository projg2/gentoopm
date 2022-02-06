#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

"""
Utility functions for gentoopm.
"""

import collections
from abc import ABCMeta

try:
    exec(
        '''
class ABCObject(object, metaclass = ABCMeta):
	""" A portably-defined object with ABCMeta metaclass. """
	pass
'''
    )
except SyntaxError:  # py2
    exec(
        '''
class ABCObject(object):
	""" A portably-defined object with ABCMeta metaclass. """
	__metaclass__ = ABCMeta
'''
    )


class FillMissingNotEqual(object):
    """
    A base class filling '!=' using '=='.
    """

    def __ne__(self, other):
        return not self == other


class StringifiedComparisons(FillMissingNotEqual):
    """
    A base class with '==', '!=' and hashing methods set to use the object
    stringification.
    """

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)


class FillMissingComparisons(FillMissingNotEqual):
    """
    A base class filling '!=', '>', '<=' and '>=' comparators with '<' and
    '=='.

    @note: py2.7 and 3.2 have nice things for that already.
    """

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


class BoolCompat(object):
    """
    A base class providing __bool__() compat for Python2.
    """

    def __nonzero__(self):
        return self.__bool__()


try:

    class StringCompat(unicode):
        """
        A helper class to create objects inheriting from string. It is basically
        like subclassing str directly but with a nice C{repr()}.
        """

        def __repr__(self):
            return "%s(%s)" % (self.__class__.__name__, repr(unicode(self)))

except NameError:

    class StringCompat(str):
        """
        A helper class to create objects inheriting from string. It is basically
        like subclassing str directly but with a nice C{repr()}.
        """

        def __repr__(self):
            return "%s(%s)" % (self.__class__.__name__, repr(str(self)))


class _SpaceSepIter(object):
    def __getitem__(self, k):
        if isinstance(k, str):
            for i in self:
                if i == k:
                    return i
            else:
                raise KeyError("No item matches %s" % repr(k))
        return tuple.__getitem__(self, k)

    def __str__(self):
        return " ".join(self)


class SpaceSepTuple(tuple, _SpaceSepIter):
    """
    A tuple subclass representing a space-separated list.
    """

    def __new__(self, s):
        if isinstance(s, str):
            s = s.split()
        return tuple.__new__(self, s)


class SpaceSepFrozenSet(frozenset, _SpaceSepIter):
    """
    A frozenset subclass representing a space-separated list.
    """

    def __new__(self, s):
        if isinstance(s, str):
            s = s.split()
        return frozenset.__new__(self, s)


def EnumTuple(name, *keys):
    """
    Create a namedtuple factory for an enumerated type. The resulting factory
    function shall be called with keyword argument with names resembling
    enumerated value names and values evaluating to True or False.

    >>> MyTestEnum = EnumTuple('MyTestEnum', 'bad', 'good')
    >>> i = 4
    >>> MyTestEnum(bad = i <= 3, good = i > 3)
    MyTestEnum(bad=False, good=True)

    @param name: name of the resulting namedtuple
    @type name: string
    @param keys: list of enumerated values
    @type keys: strings
    @return: Factory function creating namedtuples.
    @rtype: func(**kwargs)
    """

    def _check_args(kwargs):
        res = False
        for a in kwargs.values():
            if not isinstance(a, bool):
                raise ValueError("Non-bool passed to EnumTuple")
            if a and res:
                raise ValueError("More than a single True passed to EnumTuple")
            res |= a
        if not res:
            raise ValueError("All values passed to EnumTuple are False")
        return kwargs

    nt = collections.namedtuple(name, keys)
    return lambda **kwargs: nt(**_check_args(kwargs))
