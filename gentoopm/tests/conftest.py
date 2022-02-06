import os
import os.path
import shutil
import tempfile


test_root = tempfile.TemporaryDirectory()
shutil.copytree("test-root", test_root.name, symlinks=True, dirs_exist_ok=True)

abs_test_dir = os.path.abspath(test_root.name)
make_conf = os.path.join(abs_test_dir, "etc/portage/make.conf")
repos_conf = os.path.join(abs_test_dir, "etc/portage/repos.conf")
portdir = os.path.join(abs_test_dir, "usr/portage")

with open(os.path.join(make_conf), "a") as f:
    f.write(f"ROOT={abs_test_dir!r}\nPORTDIR={portdir!r}\n")
with open(os.path.join(repos_conf), "w") as f:
    f.write(f"[gentoo]\nlocation={portdir}\n")

# Portage is influenced by a lot of envvars, so sanitize the env
for k in list(os.environ):
    if k not in ("PATH", "PACKAGE_MANAGER") and not k.startswith("SANDBOX_"):
        del os.environ[k]
os.environ["PORTAGE_CONFIGROOT"] = abs_test_dir


def pytest_sessionfinish(session, exitstatus):
    test_root.cleanup()
