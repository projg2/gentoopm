#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.basepm.stack import PMRepoStackWrapper
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

		@type: string
		"""
		pass

	@abstractmethod
	def reload_config(self):
		"""
		(Re-)load the configuration of a particular package manager. Set up
		internal variables.

		Called by default L{__init__()}.
		"""
		pass

	def __init__(self):
		self.reload_config()

	@abstractproperty
	def repositories(self):
		"""
		Currently enabled ebuild repositories.

		@type: L{PMRepositoryDict}
		"""
		pass

	@abstractproperty
	def installed(self):
		"""
		Repository with installed packages (vardb).

		@type: L{PMRepository}
		"""
		pass

	@property
	def stack(self):
		"""
		Return a PMRepository providing access to the stacked packages in all
		ebuild repositories. It returns packages from all the repos.

		@type: L{PMRepoStackWrapper}
		"""
		return PMRepoStackWrapper(self.repositories)

	@abstractproperty
	def Atom(self):
		"""
		The PM-specific atom class.

		@type: L{PMAtom}
		"""
		pass

	@abstractproperty
	def config(self):
		"""
		The PM config instance.

		@type: L{PMConfig}
		"""
		pass
