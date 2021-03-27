#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011-2020 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

PV = '0.3.3'

"""
The package version.

@type: string
"""

def get_package_manager():
	"""
	Get the PackageManager instance for the best package manager available.
	Takes user preferences into consideration.

	@return: Best package manager instance available
	@rtype: L{PackageManager}
	@raise Exception: No package manager could be imported.
	"""

	from .preferences import get_preferred_pms
	from .submodules import get_any_pm

	return get_any_pm(get_preferred_pms())
