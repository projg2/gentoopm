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

	def _try(self, f, args):
		try:
			f(self, *args)
		except Exception as e:
			if isinstance(e.args[0], str):
				raise e.__class__('[%s] %s' % (self._pm.name, e.args[0]),
						*e.args[1:])
			else:
				raise

	def assertEqual(self, *args):
		self._try(unittest.TestCase.assertEqual, args)

	def assertNotEqual(self, *args):
		self._try(unittest.TestCase.assertNotEqual, args)

	def assertTrue(self, *args):
		self._try(unittest.TestCase.assertTrue, args)

	def assertFalse(self, *args):
		self._try(unittest.TestCase.assertFalse, args)

	def assertRaises(self, *args):
		self._try(unittest.TestCase.assertRaises, args)

class PMTestSuiteFactory(object):
	def __init__(self, pm):
		self._pm = pm

	def __call__(self, tests):
		tests = list(tests)
		for t in tests:
			t.pm = self._pm
		return unittest.TestSuite(tests)

class PMTestLoader(unittest.TestLoader):
	def __init__(self, pm):
		self.suiteClass = PMTestSuiteFactory(pm)
		unittest.TestLoader.__init__(self)

	def loadTestsFromModule(self, mod):
		if isinstance(mod, str):
			mod = __import__(mod, fromlist=['.'], level=-1)
		return unittest.TestLoader.loadTestsFromModule(self, mod)

class PackageNames(object):
	"""
	A container for package names used in tests. Supposed to allow simple
	switch to another packages when one of them stops to work.
	"""

	single = 'coreutils'
	""" Incomplete atom matching a single package. """

	single_complete = 'sys-apps/coreutils'
	""" Complete atom matching a single package. """

	multiple = 'pms'
	""" Incomplete atom matching multiple packages. """

	empty = 'example/example'
	""" Atom matching no packages. """

	repository = 'gentoo'
	""" Repository name guaranteed to match. """

	envsafe_metadata_key = 'DESCRIPTION'
	""" Metadata key which should be safe to match with environment.bz2. """
