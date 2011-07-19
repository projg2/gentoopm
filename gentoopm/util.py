#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

"""
Utility functions for gentoopm.
"""

from abc import ABCMeta, abstractmethod

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

class StringifiedComparisons(object):
	"""
	A base class with '==', '!=' and hashing methods set to use the object
	stringification.
	"""

	def __hash__(self):
		return hash(str(self))

	def __eq__(self, other):
		return str(self) == str(other)

	def __ne__(self, other):
		return str(self) != str(other)

class FillMissingNotEqual(object):
	"""
	A base class filling '!=' using '=='.
	"""

	def __ne__(self, other):
		return not self == other

class FillMissingComparisons(FillMissingNotEqual):
	"""
	A base class filling '!=', '>', '<=' and '>=' comparators with '<' and
	'=='.

	@note: py2.7 and 3.2 have nice things for that already.
	"""

	def __le__(self, other):
		return self < other or self == other

	def __gt__(self, other):
		return not self <= other

	def __ge__(self, other):
		return not self < other

class BoolCompat(object):
	"""
	A base class providing __bool__() compat for Python2.
	"""

	def __nonzero__(self):
		return self.__bool__()

class StringWrapper(StringifiedComparisons, BoolCompat):
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

	def __repr__(self):
		return '(%s)' % repr(str(self))
