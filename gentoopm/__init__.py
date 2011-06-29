#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

PV = '0'

def get_package_manager():
	"""
	Get the PackageManager instance for the best package manager available.
	Takes user preferences into consideration. Raises an exception if no PM
	could be found.
	"""

	from gentoopm.preferences import get_preferred_pms
	from gentoopm.submodules import get_any_pm

	return get_any_pm(get_preferred_pms())
