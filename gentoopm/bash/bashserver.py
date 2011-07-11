#!/usr/bin/python
#	vim:fileencoding=utf-8
# (c) 2011 Michał Górny <mgorny@gentoo.org>
# Released under the terms of the 2-clause BSD license.

import shutil, subprocess, tempfile

from gentoopm.bash import BashParser

_bash_script = '''
while true; do
	(
		source %s
		while read -r __GENTOOPM_VARS; do
			eval set -- ${__GENTOOPM_VARS}
			if [[ ${#} -eq 0 ]]; then
				# reload env file
				break
			else
				printf "%%s\\0" "${@}"
			fi
		done
	)
done
'''

class BashServer(BashParser):
	"""
	Bash script parser built on backgrounded bash process.
	"""

	def __init__(self):
		self._tmpf = tempfile.NamedTemporaryFile('w+b')
		self._bashproc = subprocess.Popen(['bash', '-c',
				_bash_script % repr(self._tmpf.name)],
			stdin = subprocess.PIPE, stdout = subprocess.PIPE,
			env = {})

	def __del__(self):
		self._bashproc.terminate()
		self._bashproc.communicate()
		self._tmpf.close()

	def load_file(self, envf):
		f = self._tmpf
		f.seek(0, 0)
		f.truncate(0)
		shutil.copyfileobj(envf, f)
		f.flush()

		self._bashproc.stdin.write('\n'.encode('ASCII'))
		self._bashproc.stdin.flush()

	def _read1(self):
		f = self._bashproc.stdout
		buf = ' '
		while buf[-1] != '\0':
			buf += f.read(1)
		return buf[1:-1].decode('utf-8')

	def __getitem__(self, k):
		self._bashproc.stdin.write(('${%s}\n' % k).encode('ASCII'))
		self._bashproc.stdin.flush()

		return self._read1()

	def copy(self, *varlist):
		q = ' '.join(['"${%s}"' % v for v in varlist])
		self._bashproc.stdin.write(('%s\n' % q).encode('ASCII'))
		self._bashproc.stdin.flush()

		ret = [self._read1() for v in varlist]
		return dict(zip(varlist, ret))
