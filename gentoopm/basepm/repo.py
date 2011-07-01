#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import ABCMeta, abstractproperty

class PMRepository(object):
	"""
	Base abstract class for a single ebuild repository.
	"""
	__metaclass__ = ABCMeta

	@abstractproperty
	def name(self):
		"""
		Return the repository name (either from the repo_name file or PM
		fallback name).
		"""
		pass
