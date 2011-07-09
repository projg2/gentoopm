#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis, re

from gentoopm.basepm.atom import PMAtom

_category_wildcard_re = re.compile(r'\w')

class PaludisAtom(PMAtom):
	def _init_atom(self, s, pm, wildcards = False):
		opts = paludis.UserPackageDepSpecOptions() \
				+ paludis.UserPackageDepSpecOption.NO_DISAMBIGUATION
		if wildcards:
			opts += paludis.UserPackageDepSpecOption.ALLOW_WILDCARDS

		try:
			self._atom = paludis.parse_user_package_dep_spec(
					s, pm._env, opts,
					paludis.Filter.All())
		except (paludis.BadVersionOperatorError, paludis.PackageDepSpecError,
				paludis.RepositoryNameError):
			raise ValueError('Incorrect atom: %s' % s)

	def __init__(self, s, pm):
		try:
			self._init_atom(s, pm)
		except ValueError:
			# try */ for the category
			self._init_atom(_category_wildcard_re.sub(r'*/\g<0>', s, 1), pm, True)

	def __contains__(self, pkg):
		raise NotImplementedError('Direct atom matching not implemented in Paludis')