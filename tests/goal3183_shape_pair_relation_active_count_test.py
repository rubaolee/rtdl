from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal3183_shape_pair_relation_active_count_2026-06-03.md"


class Goal3183ShapePairRelationActiveCountTest(unittest.TestCase):
    def test_native_surface_exports_prepared_active_count(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")

        for text in (prelude, api):
            self.assertIn("rtdl_optix_count_prepared_shape_pair_relation_flags", text)
            self.assertIn("active_count_out", text)

    def test_native_count_path_skips_final_row_allocation(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static void count_shape_pair_relation_flags_with_prepared_right_optix")
        end = text.index("static void run_shape_pair_relation_flags_optix", start)
        count_body = text[start:end]

        self.assertIn("compute_shape_pair_relation_flags_with_prepared_right_optix", count_body)
        self.assertIn("requires_segment_intersection", count_body)
        self.assertIn("requires_point_containment", count_body)
        self.assertNotIn("RtdlShapePairRelationRow", count_body)
        self.assertNotIn("std::malloc", count_body)

    def test_python_runtime_binds_count_active(self) -> None:
        text = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def count_active(self, left_polygons) -> int:", text)
        self.assertIn("rtdl_optix_count_prepared_shape_pair_relation_flags", text)
        self.assertIn("Loaded OptiX backend library does not export", text)

    def test_spatial_rayjoin_count_mode_uses_active_count(self) -> None:
        text = APP.read_text(encoding="utf-8")

        self.assertIn("prepared.count_active(packed_left)", text)
        self.assertIn("overlay_active_pair_dependency_count", text)
        self.assertIn("active_seed_count", text)
        self.assertIn("full_pair_dependency_rows", text)

    def test_report_records_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "active relation-row count",
            "skips final host row allocation",
            "does not produce device-resident relation-row columns",
            "true_zero_copy_claim_authorized: False",
            "public_speedup_claim_authorized: False",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
