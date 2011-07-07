#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import paludis

from gentoopm.basepm.atom import PMAtom

class PaludisAtom(PMAtom):
	def __init__(self, s, pm):
		try:
			self._atom = paludis.parse_user_package_dep_spec(
					s, pm._env,
					paludis.UserPackageDepSpecOptions(),
					paludis.Filter.All())
		except (paludis.BadVersionOperatorError, paludis.PackageDepSpecError):
			raise ValueError('Incorrect atom: %s' % s)
		except paludis.AmbiguousPackageNameError:
			raise KeyError('Ambiguous atom: %s' % s)
		except paludis.NoSuchPackageError:
			raise KeyError('Unable to expand atom: %s' % s)

	def __contains__(self, pkg):
		raise NotImplementedError('Direct atom matching not implemented in Paludis')
