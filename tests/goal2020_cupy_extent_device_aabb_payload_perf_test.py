from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal2020_cupy_extent_device_aabb_payload_perf_2026-05-14.md"
ARTIFACTS = (
    ROOT / "docs" / "reports" / "goal2020_pod_cupy_extent_device_aabb_payload_2048.json",
    ROOT / "docs" / "reports" / "goal2020_pod_cupy_extent_device_aabb_payload_4096.json",
    ROOT / "docs" / "reports" / "goal2020_pod_cupy_extent_device_aabb_payload_8192.json",
)
GOAL1969 = ROOT / "docs" / "reports" / "goal1969_pod_cupy_extent_polygon_control_perf.json"


class Goal2020CuPyExtentDeviceAabbPayloadPerfTest(unittest.TestCase):
    def test_cupy_extent_path_builds_device_payload_without_python_set_roundtrip(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("def _partner_pair_payload_table_cupy_extent", text)
        self.assertIn('candidate_backend == "cupy_extent" and partner == "cupy"', text)
        self.assertIn("left_indices.astype(cp.int32, copy=False)", text)
        self.assertIn("right_indices.astype(cp.int32, copy=False)", text)
        self.assertIn("aabb_pair_overlap_summary_2d_partner_columns", text)
        self.assertIn("_positive_candidate_pairs_cupy_extent", text)

    def test_pod_artifacts_record_correct_polygon_speedups_at_multiple_scales(self) -> None:
        for path in ARTIFACTS:
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows = {row["app"]: row for row in payload["results"]}

            self.assertEqual(payload["candidate_backend"], "cupy_extent")
            self.assertEqual(payload["partner"], "cupy")
            self.assertTrue(payload["all_match_v1_8_python_rtdl_oracle"])
            self.assertEqual(set(rows), {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"})
            for row in rows.values():
                self.assertTrue(row["matches_v1_8_python_rtdl_oracle"])
                self.assertLess(row["v2_vs_v1_8_ratio"], 0.25)
                self.assertGreater(row["v1_8_python_rtdl_wall"]["median_s"], 0.0)
                self.assertGreater(row["v2_rawkernel_wall"]["median_s"], 0.0)

    def test_goal2020_improves_on_goal1969_2048_baseline(self) -> None:
        old_rows = {
            row["app"]: row
            for row in json.loads(GOAL1969.read_text(encoding="utf-8"))["results"]
        }
        new_rows = {
            row["app"]: row
            for row in json.loads(ARTIFACTS[0].read_text(encoding="utf-8"))["results"]
        }

        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            self.assertLess(
                new_rows[app]["v2_vs_v1_8_ratio"],
                old_rows[app]["v2_vs_v1_8_ratio"],
            )

    def test_report_keeps_claim_boundary_tight(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic RTDL boundary", text)
        self.assertIn("not arbitrary polygon overlay", text)
        self.assertIn("not an OptiX RT-core polygon candidate-discovery claim", text)
        self.assertIn("not an absolutely fair comparison", text)
        self.assertIn("external consensus", text)


if __name__ == "__main__":
    unittest.main()
