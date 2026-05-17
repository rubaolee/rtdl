from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2258_prepared_closed_shape_membership_count_mode_2026-05-17.md"


class Goal2258PreparedClosedShapeMembershipCountModeTest(unittest.TestCase):
    def test_native_count_symbol_is_generic(self) -> None:
        symbol = "rtdl_optix_count_prepared_point_closed_shape_membership_2d"

        self.assertIn(symbol, PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(symbol, API.read_text(encoding="utf-8"))
        self.assertIn("count_prepared_point_closed_shape_membership_2d_optix", WORKLOADS.read_text(encoding="utf-8"))

    def test_python_prepared_count_surface(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def count(self, points) -> int:", runtime)
        self.assertIn("without Python row materialization", runtime)
        self.assertIn("rtdl_optix_count_prepared_point_closed_shape_membership_2d", runtime)
        self.assertIn("ctypes.POINTER(ctypes.c_size_t)", runtime)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic count-only surface", text)
        self.assertIn("not a RayJoin-specific primitive", text)
        self.assertIn("not yet", text)
        self.assertIn("No speedup claim is authorized", text)


if __name__ == "__main__":
    unittest.main()
