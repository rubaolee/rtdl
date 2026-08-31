from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
REPORT = ROOT / "docs" / "reports" / "goal3504_overlay_area_parallel_payload_prepare_2026-06-05.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3504_overlay_area_parallel_payload_prepare_pod_2026-06-05.json"


class Goal3504OverlayAreaParallelPayloadPrepareTest(unittest.TestCase):
    def test_runner_exposes_parallel_payload_prepare_evidence_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--payload-workers",
            "--parallel-payload-prepare-evidence",
            "_prepare_geometry_payload_bundle_parallel",
            "_geometry_payload_parts_worker",
            "parallel_geometry_payload_prepare",
            "geometry_plus_payload_prepare",
            "rtdl.goal3504.overlay_area_parallel_payload_prepare.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_parallel_path_is_opt_in(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("parser.add_argument(", text)
        self.assertIn('"--payload-workers"', text)
        self.assertIn("default=1", text)
        self.assertIn("parallel_payload_prepare_used = payload_workers > 1", text)

    def test_report_documents_parallel_payload_prepare_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "7.810s",
            "5.058s",
            "1.479s",
            "about 3.42x",
            "does not make prepared-payload construction device-native",
            "does not authorize",
            "release, public speedup wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pod_artifact_records_parallel_payload_prepare_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["schema"], "rtdl.goal3504.overlay_area_parallel_payload_prepare.v1")
        self.assertEqual(data["goal"], 3504)
        self.assertTrue(data["rtdl_commit"].startswith("024f3137"))
        self.assertTrue(data["parallel_payload_prepare"])
        self.assertTrue(data["parallel_payload_prepare_evidence"])
        self.assertEqual(data["payload_workers"], 8)
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["candidate_relation_row_count"], 2274)
        self.assertEqual(data["supported_relation_row_count"], 2149)
        self.assertEqual(data["component_pair_row_count"], 4524)
        self.assertEqual(data["tile_task_count"], 11617)
        self.assertEqual(data["planned_triangle_pair_count"], 4070240)
        self.assertEqual(data["executor_metadata"]["processed_triangle_pair_count"], 4070240)
        self.assertTrue(data["positive_row_count_match"])
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertEqual(data["timing_sec"]["geometry_build"], 0.0)
        self.assertEqual(data["timing_sec"]["payload_build"], 0.0)
        self.assertLess(data["timing_sec"]["parallel_geometry_payload_prepare"], 1.6)
        self.assertLess(data["timing_sec"]["geometry_plus_payload_prepare"], 1.6)
        self.assertLess(data["timing_sec"]["cupy_tile_task_executor_best_repeat"], 0.02)
        for field, value in data["claim_boundary"].items():
            with self.subTest(field=field):
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
