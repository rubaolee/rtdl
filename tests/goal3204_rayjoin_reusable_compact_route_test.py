from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"


class Goal3204RayJoinReusableCompactRouteTest(unittest.TestCase):
    def test_app_exposes_reusable_prepared_compact_route(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("class PreparedRayJoinOptixCompactGroupedCountSegments", source)
        self.assertIn("prepare_rayjoin_optix_compact_grouped_count_segments", source)
        self.assertIn("prepared_optix_compact_grouped_count_reuse", source)
        self.assertIn("prepare_static_scene_paid_once", source)
        self.assertIn("RayJoin workload interpretation, prepared-handle reuse, and left-ID remapping stay in Python", source)
        self.assertIn("candidate_device_columns(", source)
        self.assertIn("grouped_count_by_left_id_compact_device_columns", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_claim_authorized": False', source)
        self.assertIn("raise RuntimeError(\"prepared RayJoin compact grouped-count handle is closed\")", source)

    def test_reusable_handle_does_not_add_native_app_specific_symbols(self) -> None:
        source = APP.read_text(encoding="utf-8")
        class_start = source.index("class PreparedRayJoinOptixCompactGroupedCountSegments")
        class_end = source.index("def prepare_rayjoin_optix_compact_grouped_count_segments", class_start)
        body = source[class_start:class_end]

        self.assertNotIn("rtdl_optix_rayjoin", body)
        self.assertNotIn("rtdl_optix_run_rayjoin", body)
        self.assertIn("prepare_segment_pair_intersection_optix", body)
        self.assertIn("pack_segments", body)

    def test_readme_documents_reusable_python_handle_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")

        for phrase in (
            "prepared Python handle",
            "right-side scene is built once",
            "prepare_rayjoin_optix_compact_grouped_count_segments",
            "include_rows=False",
            "generic segment-pair candidate columns",
            "generic compact grouped-count",
            "columns; RayJoin route policy",
            "RayJoin route policy, left-ID remapping, and repeated-query reuse",
            "remain in Python",
        ):
            self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
