#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class PackageManager(ABCObject):
	"""
	Base abstract class for a package manager.
	"""

	@abstractproperty
	def name(self):
		"""
		Return the canonical name of the PM. The value should be static
		and unique.
		"""
		pass

	@abstractmethod
	def reload_config(self):
		"""
		(Re-)load the configuration of a particular package manager. Set up
		internal variables.

		Called by default __init__().
		"""
		pass

	def __init__(self):
		self.reload_config()

	@abstractproperty
	def repositories(self):
		"""
		Return an PMRepositoryDict (gentoopm.basepm.repo.PMRepositoryDict)
		subclass referring to the currently enabled ebuild repositories.
		"""
		pass

	@abstractproperty
	def installed(self):
		"""
		Return a PMRepository for installed packages (vardb).
		"""
		pass
