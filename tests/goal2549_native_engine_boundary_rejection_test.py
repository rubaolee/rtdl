from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SYMBOL = "rtdl_optix_aggregate_frontier_inverse_square_scalar_sum_3d_device"
PY_SYMBOL = "OPTIX_AGGREGATE_FRONTIER_INVERSE_SQUARE_SCALAR_SUM_3D_DEVICE_SYMBOL"
REPORT = REPO_ROOT / "docs" / "reports" / "goal2549_native_optix_aggregate_frontier_scalar_3d_2026-05-23.md"
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"


class Goal2549NativeEngineBoundaryRejectionTest(unittest.TestCase):
    def test_rejected_force_law_symbol_is_not_exported(self) -> None:
        checked_paths = [
            REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h",
            REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
            REPO_ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp",
            REPO_ROOT / "src" / "rtdsl" / "optix_runtime.py",
            REPO_ROOT / "src" / "rtdsl" / "__init__.py",
        ]
        for path in checked_paths:
            with self.subTest(path=path.name):
                text = path.read_text()
                self.assertNotIn(SYMBOL, text)
                self.assertNotIn(PY_SYMBOL, text)

    def test_rejection_is_documented(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        self.assertIn("rejected", report_text.lower())
        self.assertIn("hardcoded", report_text)
        self.assertIn("source_weight * target_or_aggregate_weight / distance^2", report_text)
        self.assertIn("Goal2549 rejected", readme_text)
        self.assertIn("app-independent engine", readme_text)


if __name__ == "__main__":
    unittest.main()
