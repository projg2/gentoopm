# (c) 2011-2024 Michał Górny <mgorny@gentoo.org>
# SPDX-License-Identifier: GPL-2.0-or-later

import pytest


def test_userpriv(pm):
    if not pm.config.userpriv_enabled:
        pytest.skip("userpriv disabled")
    assert pm.config.userpriv_uid != 0
    assert pm.config.userpriv_gid != 0
