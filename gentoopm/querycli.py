#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import argparse, os.path
from abc import abstractmethod

from gentoopm import get_package_manager
from gentoopm.util import ABCObject

def _reponame(val):
	"""
	Check the value for correctness as repository name. In fact, it only ensures
	it isn't a path so that it won't confuse pm.repositories[val].

	@param val: the config option value
	@type val: string
	@return: whether the value is a correct repo name
	@rtype: bool
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

		@return: the help string
		@rtype: string
		"""
		descdoc = ' '.join(self.__doc__.split())
		descdoc = descdoc[0].lower() + descdoc[1:]
		return descdoc.rstrip('.')

	def __init__(self, argparser):
		"""
		Instantiate the subcommand, setting argument parser as necessary.

		@param argparser: sub-command argument parser
		@type argparser: C{argparse.ArgumentParser}
		"""
		argparser.set_defaults(instance = self)
		self._arg = argparser

	@abstractmethod
	def __call__(self, pm, args):
		"""
		Call the sub-command, passing pm (a working PackageManager instance)
		and args (the result of argument parsing). Can return exit code
		for the process if relevant. If it doesn't, 0 will be used.

		@param pm: package manager instance
		@type pm: L{PackageManager}
		@param args: command arguments
		@type args: C{argparse.Namespace}
		@return: Process exit code or None if irrelevant
		@rtype: bool/None
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
			argparser.add_argument('repo_name', type=_reponame,
				help='The repository name to look up')

		def __call__(self, pm, args):
			try:
				r = pm.repositories[args.repo_name]
			except KeyError:
				self._arg.error('No repository named %s' % args.repo_name)
				return 1
			print(r.path)

	class shell(PMQueryCommand):
		"""
		Run a Python shell with current PM selected.
		"""
		def __call__(self, pm, args):
			welc = "The %s PM is now available as 'pm' object." % pm.name
			kwargs = {}

			try:
				from IPython import embed
			except ImportError:
				try:
					from IPython.Shell import IPShellEmbed
				except ImportError:
					print('For better user experience, install IPython.')
					from code import InteractiveConsole
					embed = InteractiveConsole({'pm': pm}).interact
					kwargs['banner'] = welc
				else:
					embed = IPShellEmbed()
					embed.set_banner(embed.IP.BANNER + '\n\n' + welc)
			else:
				kwargs['banner2'] = welc

			embed(**kwargs)

	def __iter__(self):
		for k in dir(self):
			if k.startswith('_'):
				continue
			cls = getattr(self, k)
			yield (k.replace('_', '-'), cls.help(), cls)

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
		except Exception:
			arg.error('No working package manager could be found.')

		return args.instance(pm, args) or 0
