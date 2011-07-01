#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import ABCMeta, abstractmethod, abstractproperty

class PMRepositoryDict(object):
	"""
	A dict-like object providing access to a set of repositories.

	The repositories can be referenced through their names or paths,
	or iterated over. An access should result in an instantiated PMRepository
	subclass.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __iter__(self):
		"""
		Iterate over the repository list.
		"""
		pass

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
		Return an PMRepositoryDict subclass referring to the currently enabled
		ebuild repositories.
		"""
		pass
