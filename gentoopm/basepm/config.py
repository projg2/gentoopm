#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

from abc import abstractproperty

from ..util import ABCObject


class PMConfig(ABCObject):
    @abstractproperty
    def userpriv_enabled(self):
        """
        Check whether root privileges are dropped for build-time.

        @type: bool
        """
        pass

    @abstractproperty
    def userpriv_uid(self):
        """
        The UID used for userpriv.

        If userpriv is disabled, the result of calling this method is
        undefined. It can result in an exception.

        @type: string/numeric
        """
        pass

    @abstractproperty
    def userpriv_gid(self):
        """
        The GID used for userpriv.

        If userpriv is disabled, the result of calling this method is
        undefined. It can result in an exception.

        @type: string/numeric
        """
        pass
