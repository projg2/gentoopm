#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import bz2

from gentoopm.bash import get_any_bashparser

class LazyBashParser(object):
	"""
	Lazily-initialized, shared bash parser wrapper.
	"""
	_curr_path = None
	_parser = None

	def set_file(self, path, open_func):
		if self._curr_path == path:
			return
		self._curr_path = path
		f = open_func(path)
		if self._parser is None:
			self._parser = get_any_bashparser()
		self._parser.load_file(f)
		f.close()

	def __getitem__(self, k):
		return self._parser[k]

	def copy(self, *v):
		return self._parser.copy(*v)

	def __del__(self):
		del self._parser

_bp = LazyBashParser()

class PMPackageEnvironment(object):
	"""
	Package environment accessor class.
	"""

	def __init__(self, path, bzipped2 = False):
		self._path = path
		self._open_func = bz2.BZ2File if bzipped2 else open

	def __getitem__(self, k):
		_bp.set_file(self._path, self._open_func)
		return _bp[k]

	def copy(self, *keys):
		_bp.set_file(self._path, self._open_func)
		return _bp.copy(*keys)
