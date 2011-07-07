#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import portage.exception as pe
from portage.dbapi.dep_expand import dep_expand
from portage.dep import Atom, match_from_list
from portage.versions import catsplit

from gentoopm.basepm.atom import PMAtom

class PortageAtom(PMAtom):
	def __init__(self, s, pm):
		try:
			a = dep_expand(s, mydb = pm._portdb,
					settings = pm._portdb.settings)
		except pe.AmbiguousPackageName:
			raise KeyError('Ambiguous atom: %s' % s)
		except pe.InvalidAtom:
			raise ValueError('Incorrect atom: %s' % s)

		if catsplit(a.cp)[0] == 'null':
			raise KeyError('Unable to expand atom: %s' % s)
		self._atom = a

	def __contains__(self, pkg):
		# SLOT matching requires metadata so delay it.
		if not match_from_list(self._atom, [pkg.id]):
			return False
		return not self._atom.slot \
				or self._atom.slot == pkg.metadata.SLOT
