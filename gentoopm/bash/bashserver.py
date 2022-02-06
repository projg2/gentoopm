#!/usr/bin/python
# 	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import shutil, subprocess, tempfile

from ..exceptions import InvalidBashCodeError

from . import BashParser

_bash_script = """
while
	(
		while read -r __GENTOOPM_CMD; do
			eval ${__GENTOOPM_CMD}
		done
		exit 1
	)
do
	:
done
"""


class BashServer(BashParser):
    """
    Bash script parser built on backgrounded bash process.
    """

    def __init__(self):
        self._bashproc = subprocess.Popen(
            ["bash", "-c", _bash_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            env={},
        )

    def terminate(self):
        if self._bashproc is not None:
            self._bashproc.terminate()
            self._bashproc.communicate()
            self._bashproc = None

    def load_file(self, envf):
        with tempfile.NamedTemporaryFile("w+b") as f:
            shutil.copyfileobj(envf, f)
            f.flush()

            self._write(
                "exit 0",
                'bash -n %s &>/dev/null && printf "OK\\0" || printf "FAIL\\0"'
                % repr(f.name),
            )

            if self._read1() != "OK":
                raise InvalidBashCodeError()

            self._write('source %s &>/dev/null; printf "DONE\\0"' % repr(f.name))

            if self._read1() != "DONE":
                raise AssertionError("Sourcing unexpected caused stdout output")

    def _read1(self):
        assert self._bashproc is not None
        f = self._bashproc.stdout
        buf = b" "
        while not buf.endswith(b"\0"):
            x = f.read(1)
            if len(x) < 1:
                # end-of-file
                raise InvalidBashCodeError()
            buf += x
        return buf[1:-1].decode("utf-8")

    def _write(self, *cmds):
        assert self._bashproc is not None
        for cmd in cmds:
            self._bashproc.stdin.write(("%s\n" % cmd).encode("ASCII"))
        self._bashproc.stdin.flush()

    def _cmd_print(self, *varlist):
        q = " ".join(['"${%s}"' % v for v in varlist])
        self._write("set -- %s" % q, 'printf "%s\\0" "${@}"')
        return [self._read1() for v in varlist]

    def __getitem__(self, k):
        return self._cmd_print(k)[0]

    def __call__(self, code):
        self._write('( %s ) &>/dev/null; printf "%%d\\0" "${?}"' % code)
        return int(self._read1())

    def copy(self, *varlist):
        ret = self._cmd_print(*varlist)
        return dict(zip(varlist, ret))
