from __future__ import annotations

from pathlib import Path
import py_compile
import unittest

from scripts.v4_0_current_front_door_claim_boundary_scan import scan as scan_v4_front_door_claims


ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_INDEX = ROOT / "tutorials" / "README.md"
CURRENT_TUTORIAL = ROOT / "tutorials" / "current" / "README.md"
V4_TUTORIAL_DIR = ROOT / "tutorials" / "v4_0"
EXAMPLES_INDEX = ROOT / "examples" / "README.md"
V4_EXAMPLES_DIR = ROOT / "examples" / "v4_0"
V4_EXAMPLES_GETTING_STARTED = V4_EXAMPLES_DIR / "getting_started"

V4_TUTORIAL_FILES = (
    V4_TUTORIAL_DIR / "README.md",
    V4_TUTORIAL_DIR / "01_source_tree_gpu_setup.md",
    V4_TUTORIAL_DIR / "02_fixed_radius_cupy.md",
    V4_TUTORIAL_DIR / "03_numba_device_array_route.md",
    V4_TUTORIAL_DIR / "04_pytorch_cuda_tensor_route.md",
    V4_TUTORIAL_DIR / "05_boundaries_and_troubleshooting.md",
)

V4_EXAMPLE_FILES = (
    V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_cupy_hello.py",
    V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_numba_hello.py",
    V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_pytorch_hello.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(text: str) -> str:
    return " ".join(text.split())


class V40UserTutorialsTest(unittest.TestCase):
    def test_v4_tutorial_track_is_indexed_as_current_front_door(self) -> None:
        tutorial_index = _read(TUTORIAL_INDEX)
        examples_index = _read(EXAMPLES_INDEX)
        v4_readme = _compact(_read(V4_TUTORIAL_DIR / "README.md"))
        current_readme = _read(CURRENT_TUTORIAL)

        self.assertIn("[V4.0 Tutorial Track](v4_0/README.md)", tutorial_index)
        self.assertIn("current V4.0 Python GPU device-array operator route", tutorial_index)
        self.assertIn("v4_0/getting_started", examples_index)
        self.assertIn("current V4.0 source-tree front door", examples_index)

        for token in (
            "current V4.0.0 source-tree learner path",
            "fixed_radius_count_threshold_2d",
            "CuPy, Numba, or PyTorch owns CUDA arrays",
            "narrow V4.0.0 source-tree front door",
            "Source-Tree GPU Setup",
            "CuPy Fixed-Radius Route",
            "Numba DeviceArray Route",
            "PyTorch CUDA Tensor Route",
            "Boundaries And Troubleshooting",
        ):
            self.assertIn(token, v4_readme)

        self.assertIn("Status: current v3.0.2 source-tree learner path.", current_readme)
        self.assertIn("V4.0 Current Track", tutorial_index)

    def test_v4_tutorial_files_exist_and_keep_blocked_claims_explicit(self) -> None:
        for path in V4_TUTORIAL_FILES:
            self.assertTrue(path.exists(), str(path))

        combined = "\n".join(_read(path) for path in V4_TUTORIAL_FILES)
        compact = _compact(combined)

        for command in (
            "PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_cupy_hello.py",
            "PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_numba_hello.py",
            "PYTHONPATH=src:. python examples/v4_0/getting_started/v4_fixed_radius_pytorch_hello.py",
        ):
            self.assertIn(command, combined)

        for blocked_boundary in (
            "does not authorize",
            "package install, PyPI, wheel, or stable SDK",
            "public true-zero-copy",
            "async or nonblocking completion",
            "public speedup",
            "RT-core speedup",
            "full PyTorch",
            "full Numba",
            "full DLPack",
        ):
            self.assertIn(blocked_boundary, compact)

        for forbidden_positive in (
            "stable V4 SDK",
            "RTDL is faster",
            "true zero-copy is authorized",
            "async is authorized",
        ):
            self.assertNotIn(forbidden_positive, combined)

    def test_v4_examples_compile_and_declare_claim_boundaries(self) -> None:
        for path in V4_EXAMPLE_FILES:
            self.assertTrue(path.exists(), str(path))
            py_compile.compile(str(path), doraise=True)

        cupy = _read(V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_cupy_hello.py")
        numba = _read(V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_numba_hello.py")
        pytorch = _read(V4_EXAMPLES_GETTING_STARTED / "v4_fixed_radius_pytorch_hello.py")

        for source in (cupy, numba, pytorch):
            self.assertIn("run_v4_fixed_radius_count_threshold_2d", source)
            self.assertIn('"claim_boundaries"', source)
            self.assertIn('"v4_current_front_door_authorized": True', source)
            self.assertIn('"package_install_claim_authorized": False', source)
            self.assertIn('"public_true_zero_copy_claim_authorized": False', source)
            self.assertIn('"async_claim_authorized": False', source)
            self.assertIn('"public_speedup_claim_authorized": False', source)
            self.assertIn('"rt_core_speedup_claim_authorized": False', source)

        self.assertIn('partner="cupy"', cupy)
        self.assertIn('partner="numba"', numba)
        self.assertIn('partner="torch"', pytorch)
        self.assertNotIn('partner="pytorch"', pytorch)
        self.assertIn('"full_numba_surface_claim_authorized": False', numba)
        self.assertIn('"full_pytorch_surface_claim_authorized": False', pytorch)

    def test_claim_scan_covers_v4_tutorials_and_examples_after_promotion(self) -> None:
        payload = scan_v4_front_door_claims(ROOT)

        self.assertEqual("pass", payload["status"])
        self.assertFalse(payload["findings"])
        scanned = set(payload["public_files_scanned"])

        for expected_path in (
            "tutorials/README.md",
            "tutorials/v4_0/README.md",
            "tutorials/v4_0/02_fixed_radius_cupy.md",
            "tutorials/v4_0/03_numba_device_array_route.md",
            "tutorials/v4_0/04_pytorch_cuda_tensor_route.md",
            "examples/README.md",
            "examples/v4_0/README.md",
            "examples/v4_0/getting_started/README.md",
        ):
            self.assertIn(expected_path, scanned)

        self.assertTrue(payload["claim_boundaries"]["v4_current_release_claim_authorized"])
        self.assertTrue(payload["claim_boundaries"]["v4_release_package_claim_authorized"])
        self.assertTrue(payload["claim_boundaries"]["fixed_radius_m1_python_gpu_operator_claim_authorized"])
        self.assertFalse(payload["claim_boundaries"]["stable_v4_sdk_claim_authorized"])
        self.assertFalse(payload["claim_boundaries"]["public_true_zero_copy_claim_authorized"])
        self.assertFalse(payload["claim_boundaries"]["pytorch_route_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
