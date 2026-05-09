import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal1586_v1_5_4_optix_collect_k_multi_session_validation_runner.py"


class Goal1590V154OptixCudaToolchainDiagnosticsTest(unittest.TestCase):
    def test_native_driver_error_adds_unsupported_toolchain_hint(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("cuda_driver_error_message", source)
        self.assertIn("unsupported toolchain", source)
        self.assertIn("RTDL generated PTX that this CUDA driver cannot load", source)
        self.assertIn("RTDL_OPTIX_PTX_ARCH=compute_XX", source)

    def test_python_runtime_adds_unsupported_toolchain_hint(self) -> None:
        source = PY_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("unsupported toolchain", source)
        self.assertIn("RTDL could not load generated PTX", source)
        self.assertIn("LD_LIBRARY_PATH", source)

    def test_validation_runner_has_cuda_toolchain_preflight(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("_preflight_cuda_toolchain", source)
        self.assertIn("has_cuda_compat_path", source)
        self.assertIn("Use a driver-compatible CUDA toolkit", source)


if __name__ == "__main__":
    unittest.main()
