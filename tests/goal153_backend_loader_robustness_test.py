import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl.optix_runtime as optix_runtime
import rtdsl.vulkan_runtime as vulkan_runtime


class _MissingSymbolLibrary:
    def __init__(self, path: str) -> None:
        self._rtdl_library_path = path


class Goal153BackendLoaderRobustnessTest(unittest.TestCase):
    def test_vulkan_register_argtypes_reports_stale_library_cleanly(self) -> None:
        lib = _MissingSymbolLibrary("/tmp/stale/librtdl_vulkan.so")
        with self.assertRaisesRegex(
            RuntimeError,
            "missing required export 'rtdl_vulkan_get_version'.*make build-vulkan",
        ):
            vulkan_runtime._register_argtypes(lib)

    def test_optix_register_argtypes_reports_stale_library_cleanly(self) -> None:
        lib = _MissingSymbolLibrary("/tmp/stale/librtdl_optix.so")
        with self.assertRaisesRegex(
            RuntimeError,
            "missing required export 'rtdl_optix_get_version'.*make build-optix",
        ):
            optix_runtime._register_argtypes(lib)


if __name__ == "__main__":
    unittest.main()
