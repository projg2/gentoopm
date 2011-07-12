#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from gentoopm.basepm.config import PMConfig

class PaludisConfig(PMConfig):
	def __init__(self, env):
		self._env = env
