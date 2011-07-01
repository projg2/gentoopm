#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractproperty

from gentoopm.util import ABCObject

class PMRepository(ABCObject):
	"""
	Base abstract class for a single ebuild repository.
	"""

	@abstractproperty
	def name(self):
		"""
		Return the repository name (either from the repo_name file or PM
		fallback name).
		"""
		pass

	@abstractproperty
	def path(self):
		"""
		Return the canonical path to the ebuild repository.
		"""
		pass
