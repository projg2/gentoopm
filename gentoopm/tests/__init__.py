#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import unittest

class PMTestCase(unittest.TestCase):
	_pm = None

	@property
	def pm(self):
		assert(self._pm is not None)
		return self._pm

	@pm.setter
	def pm(self, val):
		assert(self._pm is None)
		self._pm = val

class PMTestSuiteFactory(object):
	def __init__(self, pm):
		self._pm = pm

	def __call__(self, tests):
		for t in tests:
			t.pm = self._pm
		return unittest.TestSuite(tests)

class PMTestLoader(unittest.TestLoader):
	def __init__(self, pm):
		self.suiteClass = PMTestSuiteFactory(pm)
		unittest.TestLoader.__init__(self)

	def loadTestsFromModule(self, mod):
		if isinstance(mod, basestring):
			mod = __import__(mod, fromlist=['.'], level=-1)
		return unittest.TestLoader.loadTestsFromModule(self, mod)

class PackageNames(object):
	"""
	A container for package names used in tests. Supposed to allow simple
	switch to another packages when one of them stops to work.
	"""

	single = 'portage'
	""" Incomplete atom matching a single package. """

	single_complete = 'sys-apps/portage'
	""" Complete atom matching a single package. """

	multiple = 'pms'
	""" Incomplete atom matching multiple packages. """
