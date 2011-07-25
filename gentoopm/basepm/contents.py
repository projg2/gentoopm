#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import os.path
from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject, StringCompat

class PMContentObj(StringCompat):
	def __init__(self, path):
		self._path = os.path.normpath(path)

	def __str__(self):
		return self._path

class PMPackageContents(ABCObject):
	"""
	A base class for package contents (files installed by a package).
	"""

	@abstractmethod
	def __iter__(self):
		"""
		Iterate over files and directories installed by the package.
		"""
		pass

	def __contains__(self, path):
		"""
		Check whether the path given is installed by the package.

		@param path: the path to check
		@type path: string
		@return: whether the path exists in package contents
		@rtype: bool
		"""

		path = os.path.normpath(path)
		for f in self:
			if str(f) == path:
				return True
		return False
