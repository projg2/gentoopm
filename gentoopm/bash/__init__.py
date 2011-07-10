#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

class BashParser(ABCObject):
	"""
	A base class for bash script parsing facility.
	"""

	@abstractmethod
	def load_file(self, f):
		"""
		Load and execute the contents of file.

		@param f: the file to execute
		@type f: file
		"""
		pass

	@abstractmethod
	def __getitem__(self, k):
		"""
		Get the value of an environment variable.

		@param k: environment variable name
		@type k: string
		@return: value of the environment variable (or C{''} if unset)
		@rtype: string
		"""
		pass

	def get_env(self, *varlist):
		"""
		Get values of multiple environment variables, and return them
		as a dict.

		@param varlist: environment variable names
		@type varlist: list(string)
		@return: environment variables with values
		@rtype: dict(string -> string)
		"""

		out = {}
		for v in varlist:
			out[v] = self[v]
		return out
