#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os

# portage comes last as it is often installed aside anyway
# pkgcore is best supported and fastest ATM
default_preference_list = ("pkgcore", "paludis", "portage")


def get_preferred_pms():
    """
    Find out what are the user's PM preferences and return the preferred PM
    names as an iterable, with the most preferred one coming first.

    @return: Preferred PMs, in order
    @rtype: iterable(string)
    """

    ret = []
    if "PACKAGE_MANAGER" in os.environ:
        ret.append(os.environ["PACKAGE_MANAGER"])
    for pm in default_preference_list:
        if pm not in ret:
            ret.append(pm)
    return ret
