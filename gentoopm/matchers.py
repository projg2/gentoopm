#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from .basepm.filter import PMKeywordMatcher

import re


class RegExp(PMKeywordMatcher):
    """
    A keyword attribute matcher using a regular expression.
    """

    def __init__(self, regexp):
        """
        Instantiate the regexp matcher.

        @param regexp: a regular expression to match values against
        @type regexp: string/compiled regexp
        """
        if not hasattr(regexp, "match"):
            regexp = re.compile(regexp)
        self._re = regexp

    def __eq__(self, val):
        return bool(self._re.match(str(val)))


class Contains(PMKeywordMatcher):
    """
    A keyword attribute matcher checking for list membership.
    """

    def __init__(self, *elems):
        """
        Instantiate the matcher for arguments. If multiple arguments are passed
        in, at least one of them must be contained in the value.

        @param elems: elements to match against the value contents
        @type elems: any
        """

        self._simple_matchers = set()
        self._complex_matchers = []
        for e in elems:
            if isinstance(e, str):
                self._simple_matchers.add(e)
            else:
                self._complex_matchers.append(e)

    def __eq__(self, val):
        for n in self._simple_matchers:
            if n in val:
                return True

        for n in self._complex_matchers:
            for e in val:
                if n == e:
                    return True

        return False
