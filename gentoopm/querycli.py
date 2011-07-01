#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import argparse, os.path
from abc import abstractmethod

from gentoopm import get_package_manager
from gentoopm.util import ABCObject

def reponame(val):
	"""
	Check the value for correctness as repository name. In fact, it only ensures
	it isn't a path so that it won't confuse pm.repositories[val].
	"""
	if os.path.isabs(val):
		raise ValueError('Invalid repository name: %s' % val)
	return val

class PMQueryCommand(ABCObject):
	""" A single gentoopmq command. """

	@classmethod
	def help(self):
		"""
		Return the help string for a sub-command.
		"""
		descdoc = ' '.join(self.__doc__.split())
		return descdoc.rstrip('.')

	def __init__(self, argparser):
		"""
		Instantiate the subcommand, setting argument parser as necessary.
		"""
		argparser.set_defaults(instance = self)
		self._arg = argparser

	@abstractmethod
	def __call__(self, pm, args):
		"""
		Call the sub-command, passing pm (a working PackageManager instance)
		and args (the result of argument parsing). Can return exit code
		for the process if relevant. If it doesn't, 0 will be used.
		"""
		pass

class PMQueryCommands(object):
	""" The container of all standard gentoopmq commands. """

	class package_manager(PMQueryCommand):
		"""
		Get the name of a working, preferred PM.
		"""
		def __call__(self, pm, args):
			print(pm.name)

	class repositories(PMQueryCommand):
		"""
		Print the list of ebuild repositories.
		"""
		def __call__(self, pm, args):
			return ' '.join([r.name for r in pm.repositories])

	class repo_path(PMQueryCommand):
		"""
		Print the path to the named repository.
		"""
		def __init__(self, argparser):
			PMQueryCommand.__init__(self, argparser)
			argparser.add_argument('repo_name', type=reponame,
				help='The repository name to look up')

		def __call__(self, pm, args):
			try:
				r = pm.repositories[args.repo_name]
			except KeyError:
				self._arg.error('No repository named %s' % args.repo_name)
				return 1
			print(r.path)

	def __iter__(self):
		for k in dir(self):
			if k.startswith('_'):
				continue
			cls = getattr(self, k)
			yield (k, cls.help(), cls)

class PMQueryCLI(object):
	""" A CLI for gentoopmq. """
	def __init__(self):
		self.argparser = arg = argparse.ArgumentParser()

		subp = arg.add_subparsers(title = 'Sub-commands')
		for cmd_name, cmd_help, cmd_class in PMQueryCommands():
			p = subp.add_parser(cmd_name, help=cmd_help)
			cmd_class(p)

	def main(self, argv):
		arg = self.argparser
		arg.prog = os.path.basename(argv[0])
		args = arg.parse_args(argv[1:])

		try:
			pm = get_package_manager()
		except Exception as e:
			arg.error('No working package manager could be found.')

		return args.instance(pm, args) or 0
