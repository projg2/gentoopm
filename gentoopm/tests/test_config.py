#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011-2022 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pytest


def test_userpriv(pm):
    if not pm.config.userpriv_enabled:
        pytest.skip("userpriv disabled")
    assert pm.config.userpriv_uid != 0
    assert pm.config.userpriv_gid != 0
