from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3846_stress_probe_candidates_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3846_stress_probe_candidates_a5000"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / f"{name}.json").read_text(encoding="utf-8"))


class Goal3846StressProbeCandidatesTest(unittest.TestCase):
    def test_raydb_large_rows_show_fused_primitive_hot_path_is_not_the_next_bottleneck(self) -> None:
        count = _load("raydb_count_4m_repeat50")
        total = _load("raydb_sum_4m_repeat50")

        for payload, mode in ((count, "count"), (total, "sum")):
            self.assertEqual(payload["app"], "raydb_style_columnar_aggregate")
            self.assertEqual(payload["backend"], "paper_rt_optix_v2_5_primitive_first")
            self.assertEqual(payload["mode"], mode)
            self.assertEqual(payload["row_count"], 4_194_304)
            self.assertTrue(payload["matches_cpu_reference"])
            metadata = payload["metadata"]
            self.assertEqual(metadata["prepared_internal_repeat"], 50)
            self.assertEqual(metadata["prepared_internal_warmup"], 5)
            self.assertEqual(metadata["generic_primitive_reduction"], mode)
            self.assertEqual(
                metadata["native_symbol"],
                "rtdl_optix_static_triangle_scene_3d_ray_batch_prepared_primitive_grouped_i64_reduction",
            )
            self.assertFalse(metadata["typed_hit_stream_forced"])
            self.assertFalse(metadata["native_device_hit_stream_columns_ready"])

        self.assertLess(count["elapsed_sec"], 0.01)
        self.assertLess(total["elapsed_sec"], 0.04)

    def test_librts_scale_probe_is_rt_core_accelerated_and_seconds_level(self) -> None:
        payload = _load("librts_131k_repeat10")

        self.assertEqual(payload["app"], "librts_spatial_index")
        self.assertEqual(payload["mode"], "optix_aabb_index")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertEqual(payload["fixture"]["box_count"], 131_072)
        self.assertEqual(payload["fixture"]["point_query_count"], 131_072)
        self.assertEqual(payload["fixture"]["box_query_count"], 131_072)
        protocol = payload["repeat_protocol"]
        self.assertEqual(protocol["repeat"], 10)
        self.assertEqual(protocol["warmup"], 2)
        self.assertGreater(protocol["query_sec_total"], 6.0)
        self.assertGreater(protocol["query_sec_median"], 0.5)

    def test_triangle_larger_native_probe_remains_boundary_row(self) -> None:
        payload = _load("triangle_native_8192_repeat5")

        self.assertEqual(payload["benchmark_app"], "triangle_counting")
        self.assertEqual(payload["backend"], "optix")
        self.assertEqual(payload["copies"], 8192)
        section = payload["section"]
        self.assertFalse(section["rt_core_accelerated"])
        self.assertEqual(section["optix_graph_mode"], "native")
        self.assertGreater(section["run_phases"]["query_raw_view_sec"], 0.8)
        self.assertFalse(payload["claim_boundary"]["triangle_count_rt_core_claim_authorized"])

    def test_report_records_interpretation_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3846",
            "RayDB is not the next best primitive-runtime target",
            "LibRTS is more interesting",
            "Triangle counting remains a boundary row",
            "Barnes-Hut remains a separate structural project",
            "does not authorize release action",
        ):
            self.assertIn(phrase, text)

        for path in ARTIFACT_DIR.glob("*.stderr.txt"):
            self.assertEqual(path.read_text(encoding="utf-8"), "", path.name)


if __name__ == "__main__":
    unittest.main()
