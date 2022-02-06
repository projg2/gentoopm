#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod
from operator import attrgetter
import itertools

from ..util import ABCObject, FillMissingNotEqual


class PMPackageMatcher(ABCObject):
    """
    Base class for a package matcher.

    Package matcher is basically a function (or function class wrapper) which
    checks the package for match.
    """

    @abstractmethod
    def __call__(self, pkg):
        """
        Check whether a package matches the condition specified in the matcher.

        @return: True if the package matches
        @rtype: bool
        """
        pass


class PMKeywordMatcher(ABCObject, FillMissingNotEqual):
    """
    Base class for a keyword matcher.

    A keyword matcher is a condition passed as an keyword argument
    to the L{pkgset.PMPackageSet.filter()} function. It's basically an object
    which will be compared against metadata value using C{==} operator.

    @todo: Needs adjusting for new metadata accessors.
    """

    @abstractmethod
    def __eq__(self, val):
        """
        Check whether the value of a metadata key matches the condition
        specified in the matcher.

        @return: True if metadata value matches
        @rtype: bool
        """
        pass


class SmartAttrGetter(object):
    """
    A wrapper on attrgetter, supporting dots replaced by underscores. Uses the
    first package matched to distinguish between real underscores and dots.
    """

    def __init__(self, key):
        self._k = key
        self._getter = None

    def __call__(self, obj):
        if self._getter is not None:
            return self._getter(obj)

        def get_variants(args):
            prev = None
            for a in args:
                if prev is not None:
                    yield ("%s_" % prev, "%s." % prev)
                prev = a
            else:
                yield (prev,)

        variants = itertools.product(*get_variants(self._k.split("_")))
        for v in variants:
            self._getter = attrgetter("".join(v))
            try:
                return self._getter(obj)
            except AttributeError:
                pass
        else:
            raise KeyError("Invalid keyword argument: %s" % self._k)


class PMTransformedKeywordFilter(PMPackageMatcher):
    _map = {
        "key_category": "key.category",
        "key_package": "key.package",
        "key_state": "key.state",
        "description_short": "description.short",
        "description_long": "description.long",
    }

    def __new__(self, key, val):
        from ..filters import AttributeMatch

        if key in self._map:
            key = self._map[key]
        return AttributeMatch(key, val)


def transform_keyword_filters(kwargs):
    """
    Transform a number of keyword filters into positional args.

    @param kwargs: keyword arguments, as passed
            to L{basepm.pkgset.PMPackageSet.filter()}
    @type kwargs: dict
    @return: positional arguments representing the keyword filters
    @rtype: iter(L{AttributeMatch})
    """

    return itertools.starmap(PMTransformedKeywordFilter, kwargs.items())
