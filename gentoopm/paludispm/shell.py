#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import subprocess

class CaveShellException(Exception):
	""" An error from cave command. """

	def __init__(self, retcode):
		self._retcode = retcode

class CaveShell(object):
	""" An interface to run cave as a command shell. """

	_common_argv = ('cave', '--log-level', 'silent')

	def __call__(self, *args):
		p = subprocess.Popen(self._common_argv + args,
				stdout = subprocess.PIPE)
		stdout, stderr = p.communicate()
		ret = p.wait()

		if ret != 0:
			raise CaveShellException(ret)
		return stdout

	def get_list(self, cmd, *args):
		out = self(cmd, *args)
		return out.splitlines()

	def get_metadata(self, cmd, key, obj, *args):
		return self(cmd, '--raw-name', key, '--format', '%v', obj, *args)
