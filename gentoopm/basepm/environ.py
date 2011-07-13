#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import bz2

from gentoopm.bash import get_any_bashparser

def _load_bp(bp, path, open_func):
	"""
	Load a file onto a bash parser.

	@param bp: the bash parser instance
	@type bp: L{BashParser}
	@param path: path to the environment file
	@type path: string
	@param open_func: open function for the file
	@type open_func: func(path, mode)
	"""
	f = open_func(path)
	bp.load_file(f)
	f.close()

class LazyBashParser(object):
	"""
	Lazily-initialized, shared bash parser wrapper.
	"""
	_curr_path = None
	_parser = None

	def set_file(self, path, open_func):
		"""
		Switch the currently used environment file, if necessary.

		@param path: path to the new environment file
		@type path: string
		@param open_func: open functions for the new file
		@type open_func: func(path, mode)
		"""

		if self._curr_path == path:
			return
		self._curr_path = path
		if self._parser is None:
			self._parser = get_any_bashparser()
		_load_bp(self._parser, path, open_func)

	def __getitem__(self, k):
		return self._parser[k]

	def copy(self, *v):
		return self._parser.copy(*v)

_bp = LazyBashParser()

class PMPackageEnvironment(object):
	"""
	Package environment accessor class.
	"""

	def __init__(self, path, bzipped2 = False):
		"""
		Instantiate L{PMPackageEnvironment} accessor.

		@param path: path to the environment file
		@type path: string
		@param bzipped2: whether to bunzip2 the file
		@type bzipped2: bool
		"""
		self._path = path
		self._open_func = bz2.BZ2File if bzipped2 else open

	def __getitem__(self, k):
		"""
		Get the value of an environment key by name.

		@param k: the key to access
		@type k: string
		@return: the environment variable value
		@rtype: string
		"""
		_bp.set_file(self._path, self._open_func)
		return _bp[k]

	def copy(self, *keys):
		"""
		Get a number of environment keys as a dict.

		@param keys: keys to access
		@type keys: strings
		@return: a dict of copied environment keys
		@rtype: dict(string -> string)
		"""
		_bp.set_file(self._path, self._open_func)
		return _bp.copy(*keys)

	def fork(self):
		"""
		Fork the bash parser. In other words, return a completely separate
		instance with the environment file loaded.

		@return: forked L{BashParser} instance
		@rtype: L{BashParser}
		"""
		bp = get_any_bashparser()
		_load_bp(bp, self._path, self._open_func)
		return bp
