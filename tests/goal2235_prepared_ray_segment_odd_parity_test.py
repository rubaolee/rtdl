from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PY_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
REPORT = ROOT / "docs" / "reports" / "goal2235_prepared_ray_segment_odd_parity_2026-05-17.md"


class Goal2235PreparedRaySegmentOddParityTest(unittest.TestCase):
    def test_native_compact_odd_parity_symbol_is_generic(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        symbol = "rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d"
        self.assertIn(symbol, prelude)
        self.assertIn(symbol, api)
        self.assertIn("run_prepared_ray_segment_group_odd_parity_2d_optix", api)
        for forbidden in ("pip", "rayjoin", "polygon", "county", "spatial_join"):
            self.assertNotIn(forbidden, symbol)

    def test_workload_filters_even_parity_before_output(self) -> None:
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("bool odd_parity_only", workloads)
        self.assertIn("if (odd_parity_only && ((hit_count & 1u) == 0u))", workloads)
        self.assertIn("run_prepared_ray_segment_group_odd_parity_2d_optix", workloads)
        self.assertIn("finalize_ray_segment_group_count_rows(", workloads)
        self.assertIn("true,", workloads)

    def test_python_prepared_object_exposes_odd_parity_method(self) -> None:
        text = PY_RUNTIME.read_text(encoding="utf-8")
        self.assertIn("def run_odd_parity(self, rays)", text)
        self.assertIn('"rtdl_optix_run_prepared_ray_segment_group_odd_parity_2d"', text)
        self.assertIn("def _run_with_symbol(self, rays, symbol_name: str)", text)

    def test_report_keeps_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal2235", text)
        self.assertIn("odd parity", text)
        self.assertIn("app-agnostic", text)
        self.assertIn("does not authorize", text)
        self.assertIn("not a RayJoin reproduction claim", text)


if __name__ == "__main__":
    unittest.main()
