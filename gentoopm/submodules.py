#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

_supported_pms = {
    "paludis": ("paludispm", "PaludisPM"),
    "pkgcore": ("pkgcorepm", "PkgCorePM"),
    "portage": ("portagepm", "PortagePM"),
}


def get_pm(pm_name):
    """
    Get the PackageManager instance for a particularly named PM.

    @param pm_name: name of package manager to use
    @type pm_name: string
    @return: A package manager instance
    @rtype: L{PackageManager}
    @raise KeyError: pm_name doesn't refer to a supported PM
    @raise ImportError: modules required for the PM are not available
    @raise NameError: PM class is not available
    """

    modname, clsname = _supported_pms[pm_name]
    mod = __import__(modname, fromlist=[clsname], globals=globals(), level=1)
    return getattr(mod, clsname)()


def get_any_pm(pm_list):
    """
    Get the first working PackageManager from the pm_list. This function will
    try to import them in order and return the first succeeding.

    @param pm_list: list of preferred package manager names, in order
    @type pm_list: iterable(string)
    @return: Best available package manager instance
    @rtype: L{PackageManager}
    @raise Exception: if none of the PMs are available
    """

    for pm_name in pm_list:
        try:
            return get_pm(pm_name)
        except Exception:
            pass

    raise Exception("None of the requested Package Managers is available.")
