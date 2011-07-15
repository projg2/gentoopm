#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from distutils.core import setup, Command

import os.path, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
try:
	from gentoopm import PV
except ImportError:
	PV = 'unknown'

class DocCommand(Command):
	description = 'create HTML docs'
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		print('Creating API docs')
		subprocess.check_call(['epydoc', '--verbose', '--html',
			'--output', 'doc', 'gentoopm'])

class TestCommand(Command):
	description = 'run tests'
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		import unittest, doctest
		import gentoopm.submodules, gentoopm.tests

		maintestsuite = unittest.TestSuite()

		for pm in gentoopm.submodules._supported_pms:
			try:
				pm_inst = gentoopm.submodules.get_pm(pm)
			except ImportError:
				print('%s not available, skipping tests.' % pm)
			else:
				l = gentoopm.tests.PMTestLoader(pm_inst)

				testsuite = unittest.TestSuite()
				testsuite.addTests(l.loadTestsFromModule('gentoopm.tests.atom'))
				testsuite.addTests(l.loadTestsFromModule('gentoopm.tests.config'))
				maintestsuite.addTests(testsuite)

		r = unittest.TextTestRunner()
		res = r.run(maintestsuite)
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
			'gentoopm.bash',
			'gentoopm.paludispm',
			'gentoopm.pkgcorepm',
			'gentoopm.portagepm',
			'gentoopm.tests'
		],
		scripts = [
			'gentoopmq'
		],
		
		classifiers = [
			'Development Status :: 2 - Pre-Alpha',
			'Environment :: Console',
			'Intended Audience :: System Administrators',
			'License :: OSI Approved :: BSD License',
			'Operating System :: POSIX',
			'Programming Language :: Python',
			'Topic :: System :: Installation/Setup'
		],

		cmdclass = {
			'doc': DocCommand,
			'test': TestCommand
		}
)
