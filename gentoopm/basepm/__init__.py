#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import ABCMeta, abstractproperty

class PackageManager(object):
	"""
	Base abstract class for a package manager.
	"""
	__metaclass__ = ABCMeta

	@abstractproperty
	def name(self):
		"""
		Return the canonical name of the PM. The value should be static
		and unique.
		"""
		pass
