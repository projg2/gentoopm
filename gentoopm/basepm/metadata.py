#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod, abstractproperty

from gentoopm.util import ABCObject

# Keep a list common to all PMs.
metadata_keys = (
	# mandatory ebuild-defined variables (as per PMS 7.2)
	'DESCRIPTION', 'HOMEPAGE', 'SRC_URI',
	'LICENSE', 'SLOT', 'KEYWORDS', 'IUSE',
	# optional ebuild-defined variables (PMS 7.3)
	'EAPI',
	'DEPEND', 'RDEPEND', 'PDEPEND',
	'RESTRICT', 'PROPERTIES',
	'REQUIRED_USE',
	# deprecated ebuild-defined vars (not in PMS anymore)
	'PROVIDE',
	# magic ebuild-defined vars (PMS 7.4)
	'INHERITED', 'DEFINED_PHASES'
)

class PMPackageMetadata(ABCObject):
	"""
	A dict-like object providing access to a package's metadata.
	"""

	@abstractmethod
	def __getitem__(self, key):
		"""
		Get the value of a metadata key. Return it as a string, or an empty
		string when unset.
		"""
		pass

	def __iter__(self):
		"""
		Iterate over possible metadata keys.
		"""
		return iter(metadata_keys)
