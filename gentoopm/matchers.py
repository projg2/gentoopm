#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from .basepm.filter import PMKeywordMatcher

import re

class RegExp(PMKeywordMatcher):
	"""
	A keyword attribute matcher using a regular expression.
	"""

	def __init__(self, regexp):
		"""
		Instantiate the regexp matcher.

		@param re: a regular expression to match values against
		@type re: string/compiled regexp
		"""
		if not hasattr(regexp, 'match'):
			regexp = re.compile(regexp)
		self._re = regexp

	def __eq__(self, val):
		return bool(self._re.match(str(val)))

class Contains(PMKeywordMatcher):
	"""
	A keyword attribute matcher checking for list membership.
	"""

	def __init__(self, elem):
		self._elem = elem

	def __eq__(self, val):
		if isinstance(self._elem, str):
			return self._elem in val
		else:
			for e in val:
				if self._elem == e:
					return True
			return False
