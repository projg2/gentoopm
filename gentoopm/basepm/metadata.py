#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractmethod

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
	# magic ebuild-defined vars (PMS 7.4)
	'INHERITED', 'DEFINED_PHASES'
)
""" A common supported metadata key list. """

class PMPackageMetadata(ABCObject):
	"""
	A dict-like object providing access to a package's metadata.
	"""

	def __getitem__(self, key):
		"""
		Get the value of a metadata key.

		@param key: the metadata key to catch
		@type key: string
		@return: the value of a metadata key, or C{''} when unset
		@rtype: L{StringWrapper}
		@raise KeyError: when invalid metadata key referred
		"""
		try:
			return getattr(self, key)
		except AttributeError:
			raise KeyError('No metadata key named %s' % key)

	def __contains__(self, key):
		return key in metadata_keys

	@abstractmethod
	def __getattr__(self, key):
		"""
		Get the value of a metadata key through an attribute.

		@param key: the metadata key to catch
		@type key: string
		@return: the value of a metadata key, or C{''} when unset
		@rtype: L{StringWrapper}
		@raise AttributeError: when invalid metadata key referred
		"""
		pass

	def __iter__(self):
		"""
		Iterate over possible metadata keys.

		@return: available metadata keys
		@rtype: iter(L{StringWrapper})
		"""
		return iter(metadata_keys)
