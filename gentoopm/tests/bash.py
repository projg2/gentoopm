#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2015 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import io
import unittest

from gentoopm.bash.bashserver import BashServer


class BashServerTestCase(unittest.TestCase):
    basic_data = b"""
VAR1=test
VAR2="test test"
export VAR3=test
declare VAR4=test
"""

    def setUp(self):
        self._bash_server = BashServer()

    def tearDown(self):
        self._bash_server.terminate()

    def test_getitem(self):
        self._bash_server.load_file(io.BytesIO(self.basic_data))
        self.assertEqual(self._bash_server["VAR1"], "test")
        self.assertEqual(self._bash_server["VAR2"], "test test")
        self.assertEqual(self._bash_server["VAR3"], "test")
        self.assertEqual(self._bash_server["VAR4"], "test")

    def test_copy(self):
        self._bash_server.load_file(io.BytesIO(self.basic_data))
        out = self._bash_server.copy("VAR1", "VAR2", "VAR3", "VAR4")
        self.assertEqual(
            out,
            {
                "VAR1": "test",
                "VAR2": "test test",
                "VAR3": "test",
                "VAR4": "test",
            },
        )

    def test_call(self):
        data = io.BytesIO(
            b"""
test_function() {
	return 42
}
"""
        )
        self._bash_server.load_file(data)
        self.assertEqual(self._bash_server("test_function"), 42)

    def test_random_output(self):
        """Test if random output is discarded correctly."""
        data = io.BytesIO(
            b"""
echo FOO
echo BAR >&2
TEST=test
"""
        )
        self._bash_server.load_file(data)
        self.assertEqual(self._bash_server["TEST"], "test")
