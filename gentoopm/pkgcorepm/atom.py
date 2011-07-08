#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from pkgcore.util.parserestrict import parse_match

from gentoopm.basepm.atom import PMAtom

class PkgCoreAtom(PMAtom):
	def __init__(self, s):
		self._r = parse_match(s)

	def __contains__(self, pkg):
		return self._r.match(pkg._pkg)
