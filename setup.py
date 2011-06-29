#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from distutils.core import setup, Command

import os.path, sys

sys.path.insert(0, os.path.dirname(__file__))
try:
	from gentoopm import PV
except ImportError:
	PV = 'unknown'

class TestCommand(Command):
	description = 'run tests'
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		import unittest

		tests = unittest.TestSuite()

		r = unittest.TextTestRunner()
		res = r.run(tests)
		sys.exit(0 if res.wasSuccessful() else 1)

setup(
		name = 'gentoopm',
		version = PV,
		author = 'Michał Górny',
		author_email = 'mgorny@gentoo.org',
		url = 'https://github.com/mgorny/gentoopm/',

		packages = [
			'gentoopm',
			'gentoopm.basepm',
			'gentoopm.paludispm',
			'gentoopm.pkgcorepm',
			'gentoopm.portagepm'
		],
		
		classifiers = [
			'Development Status :: 1 - Planning',
			'Environment :: Console',
			'Intended Audience :: System Administrators',
			'License :: OSI Approved :: BSD License',
			'Operating System :: POSIX',
			'Programming Language :: Python',
			'Topic :: System :: Installation/Setup'
		],

		cmdclass = {
			'test': TestCommand
		}
)
