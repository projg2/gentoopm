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

class IterDictWrapper(object):
	"""
	A wrapper to a class providing an iterator & dict interface.
	"""

	def __init__(self, subobj):
		"""
		Instantiate the IterDictWrapper with subobj instance.
		"""
		self._subobj = subobj

	def __iter__(self):
		return iter(self._subobj)

	def __getitem__(self, k):
		return self._subobj[k]
