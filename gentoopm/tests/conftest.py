import os
import pathlib
import shutil

import pytest


# Portage is influenced by a lot of envvars, so sanitize the env
for k in list(os.environ):
    if k not in ("PATH",) and not k.startswith("SANDBOX_"):
        del os.environ[k]


@pytest.fixture(scope="session")
def test_env(tmp_path_factory):
    test_root = tmp_path_factory.mktemp("root")
    shutil.copytree("test-root", test_root, symlinks=True, dirs_exist_ok=True)

    abs_test_dir = pathlib.Path.cwd() / test_root
    make_conf = abs_test_dir / "etc/portage/make.conf"
    repos_conf = abs_test_dir / "etc/portage/repos.conf"
    portdir = abs_test_dir / "usr/portage"

    with make_conf.open("a") as f:
        f.write(f"ROOT={str(abs_test_dir)!r}\nPORTDIR={str(portdir)!r}\n")
    with repos_conf.open("w") as f:
        f.write(f"[gentoo]\nlocation={portdir!s}\n")

    os.environ["PORTAGE_CONFIGROOT"] = str(abs_test_dir)


@pytest.fixture(scope="session", params=["pkgcore", "portage"])
def pm(request, test_env):
    from gentoopm.submodules import get_pm

    try:
        return get_pm(request.param)
    except ImportError as e:
        pytest.skip(f"PM not found: {e}")
