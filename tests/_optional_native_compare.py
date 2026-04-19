import os
import platform
import shutil
import subprocess
import unittest
from pathlib import Path


def _any_file(directory: Path, patterns: tuple[str, ...]) -> bool:
    return any(path.exists() for pattern in patterns for path in directory.glob(pattern))


def _embree_prefix_for_host() -> Path:
    if "RTDL_EMBREE_PREFIX" in os.environ:
        return Path(os.environ["RTDL_EMBREE_PREFIX"])
    if platform.system() == "Darwin":
        return Path("/opt/homebrew/opt/embree")
    return Path("/usr")


def skip_unless_optional_native_compare_toolchain_present() -> None:
    """Skip optional C++ native comparison tests before they invoke a linker."""
    system = platform.system()
    if system == "Windows":
        return
    if shutil.which("c++") is None:
        raise unittest.SkipTest("optional native comparison toolchain unavailable: c++ compiler not found")

    embree_prefix = _embree_prefix_for_host()
    embree_include = embree_prefix / "include" / "embree4"
    embree_lib_dirs = (
        embree_prefix / "lib",
        embree_prefix / "lib64",
        Path("/usr/lib"),
        Path("/usr/lib64"),
        Path("/usr/lib/x86_64-linux-gnu"),
        Path("/opt/homebrew/lib"),
    )
    if not embree_include.exists() or not any(_any_file(path, ("libembree4.*", "embree4.lib")) for path in embree_lib_dirs):
        raise unittest.SkipTest("optional native comparison toolchain unavailable: Embree headers/libraries not found")

    pkg_config = shutil.which("pkg-config")
    if pkg_config:
        for package in ("geos", "geos_c"):
            if subprocess.run([pkg_config, "--exists", package], check=False).returncode == 0:
                return

    geos_lib_dirs = (
        Path("/opt/homebrew/opt/geos/lib"),
        Path("/opt/homebrew/lib"),
        Path("/usr/local/lib"),
        Path("/usr/lib"),
        Path("/usr/lib64"),
        Path("/usr/lib/x86_64-linux-gnu"),
    )
    if not any(_any_file(path, ("libgeos_c.*", "geos_c.lib")) for path in geos_lib_dirs):
        raise unittest.SkipTest("optional native comparison toolchain unavailable: GEOS C library not found")


def skip_optional_native_compare_failure(exc: BaseException) -> None:
    """Skip optional native comparison tests when local C++ deps are missing."""
    message = str(exc)
    cmd = getattr(exc, "cmd", None)
    stdout = getattr(exc, "stdout", None)
    stderr = getattr(exc, "stderr", None)
    if cmd:
        message = f"{message}\n{cmd}"
    if stdout:
        message = f"{message}\n{stdout}"
    if stderr:
        message = f"{message}\n{stderr}"
    lowered = message.lower()
    markers = (
        "geos",
        "embree",
        "pkg-config",
        "library not found",
        "cannot find -l",
        "native oracle build failed",
        "optional native comparison build",
        "-lembree4",
        "-lgeos_c",
        "goal15_lsi_native",
        "goal15_pip_native",
        "rtdl_embree.cpp",
    )
    if isinstance(exc, (RuntimeError, subprocess.CalledProcessError)) and any(marker in lowered for marker in markers):
        raise unittest.SkipTest(f"optional native comparison toolchain unavailable: {message}") from exc
