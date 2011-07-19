#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

"""
Utility functions for gentoopm.
"""

from abc import ABCMeta

try:
	exec('''
class ABCObject(object, metaclass = ABCMeta):
	""" A portably-defined object with ABCMeta metaclass. """
	pass
''')
except SyntaxError: # py2
	exec('''
class ABCObject(object):
	""" A portably-defined object with ABCMeta metaclass. """
	__metaclass__ = ABCMeta
''')

class StringWrapper(object):
	"""
	A wrapper for strings, to ensure that users stringify properties. This way,
	we can replace string-returning properties into more complex types whenever
	necessary.
	"""

	def __new__(self, s):
		if isinstance(s, StringWrapper):
			raise AssertionError('Nah, redundant.')
		if s is None:
			return None
		else:
			return object.__new__(self, s)

	def __init__(self, s):
		"""
		Instantiate.

		@param s: object to stringify when stringified
		@type s: stringifiable
		"""
		self._s = s

	def __str__(self):
		return str(self._s)

	def __bool__(self):
		return bool(str(self))

	def __nonzero__(self):
		return self.__bool__(self)

	def __repr__(self):
		return '(%s)' % repr(str(self))

	def __eq__(self, other):
		return str(self) == str(other)

	def __ne__(self, other):
		return not self.__eq__(other)
