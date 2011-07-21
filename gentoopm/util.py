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

class StringCompat(StringifiedComparisons):
	"""
	A helper class providing objects with compatibility string functions,
	working on stringified form of objects. In other words, it lets you use
	objects like strings.
	"""

	def __hasattr__(self, k):
		return hasattr(str, k)

	def __getattr__(self, k):
		return getattr(str(self), k)

	# other useful special methods
	def __add__(self, other):
		return str(self) + other

	def __contains__(self, h):
		# XXX: might be useful to override this
		return h in str(self)

	def __format__(self, spec):
		return format(str(self), spec)

	def __getitem__(self, k):
		return str(self)[k]

	def __len__(self):
		return len(str(self))

	def __mul__(self, other):
		return str(self) * other

	def __rmod__(self, other):
		return other % str(self)

	def __rmul__(self, other):
		return other * str(self)

class SpaceSepTuple(tuple):
	"""
	A tuple subclass representing a space-separated list.
	"""

	def __new__(self, s):
		if isinstance(s, str):
			s = s.split()
		return tuple.__new__(self, s)

	def __str__(self):
		return ' '.join(self)
