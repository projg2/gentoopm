#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2015-2022 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import pytest

import io

from gentoopm.bash.bashserver import BashServer


@pytest.fixture
def bash_server():
    server = BashServer()
    yield server
    server.terminate()


BASIC_DATA = b"""
VAR1=test
VAR2="test test"
export VAR3=test
declare VAR4=test
"""


def test_getitem(bash_server):
    bash_server.load_file(io.BytesIO(BASIC_DATA))
    assert bash_server["VAR1"] == "test"
    assert bash_server["VAR2"] == "test test"
    assert bash_server["VAR3"] == "test"
    assert bash_server["VAR4"] == "test"


def test_copy(bash_server):
    bash_server.load_file(io.BytesIO(BASIC_DATA))
    assert bash_server.copy("VAR1", "VAR2", "VAR3", "VAR4") == {
        "VAR1": "test",
        "VAR2": "test test",
        "VAR3": "test",
        "VAR4": "test",
    }


def test_call(bash_server):
    bash_server.load_file(
        io.BytesIO(
            b"""
test_function() {
    return 42
}
"""
        )
    )
    assert bash_server("test_function") == 42


def test_random_output(bash_server):
    """Test that random output is discarded correctly"""
    bash_server.load_file(
        io.BytesIO(
            b"""
echo FOO
echo BAR >&2
TEST=test
"""
        )
    )
    assert bash_server["TEST"] == "test"
