#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

def transform_filters(args, kwargs):
	"""
	Transform our filters into pkgcore restrictions whenever possible. Takes
	args and kwargs as passed to .filter() and returns a tuple (restriction,
	newargs, newkwargs).

	If no filters can be transformed, None is returned as restriction,
	and args & kwargs are returned unmodified.
	"""

	return (None, args, kwargs)
