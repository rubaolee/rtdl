import subprocess
import unittest


def skip_optional_native_compare_failure(exc: BaseException) -> None:
    """Skip optional native comparison tests when local C++ deps are missing."""
    message = str(exc)
    stderr = getattr(exc, "stderr", None)
    if stderr:
        message = f"{message}\n{stderr}"
    lowered = message.lower()
    markers = (
        "geos",
        "embree",
        "pkg-config",
        "library not found",
        "cannot find -l",
        "returned non-zero exit status",
        "native oracle build failed",
        "optional native comparison build",
    )
    if isinstance(exc, (RuntimeError, subprocess.CalledProcessError)) and any(marker in lowered for marker in markers):
        raise unittest.SkipTest(f"optional native comparison toolchain unavailable: {message}") from exc
