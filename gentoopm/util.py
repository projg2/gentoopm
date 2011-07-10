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
