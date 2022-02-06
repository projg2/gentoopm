#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.


class PMException(Exception):
    """
    A base class for exceptions.
    """

    pass


class EmptyPackageSetError(PMException):
    """
    Empty set passed to a function requiring a non-empty one.
    """

    pass


class AmbiguousPackageSetError(PMException):
    """
    Ambiguous package set passed, e.g. containing multiple package names when
    consistenly-named set was expected.
    """

    pass


class InvalidAtomStringError(PMException):
    """
    An invalid string was passed to the atom constructor.
    """

    pass


class InvalidBashCodeError(PMException):
    """
    An invalid code has been passed to the bash parser.
    """

    pass
