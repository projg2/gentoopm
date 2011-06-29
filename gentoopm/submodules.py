#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

supported_pms = {
	'paludis': ('gentoopm.paludispm', 'PaludisPM'),
	'pkgcore': ('gentoopm.pkgcorepm', 'PkgCorePM'),
	'portage': ('gentoopm.portagepm', 'PortagePM')
}

def get_pm(pm_name):
	"""
	Get the PackageManager instance for a particularly named PM. Either returns
	a PackageManager subclass instance or raises one of the following
	exceptions:

	- KeyError if pm_name doesn't refer to a supported PM,
	- ImportError if modules required for a particular PM are not available,
	- NameError if for some reason required class isn't provided by the module
		(consider this an internal error).
	"""

	modname, clsname = supported_pms[pm_name]
	mod = __import__(modname, fromlist=[clsname], level=-1)
	return getattr(mod, clsname)()

def get_any_pm(pm_list):
	"""
	Get the first working PackageManager from the pm_list. This function will
	try to import them in order and either return the first succeeding or raise
	an exception if all of them fail.
	"""

	for pm_name in pm_list:
		try:
			return get_pm(pm_name)
		except Exception:
			pass

	raise Exception('None of the requested Package Managers is available.')
