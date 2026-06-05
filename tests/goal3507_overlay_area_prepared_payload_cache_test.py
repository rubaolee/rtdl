from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3492_overlay_area_public_cdb_tile_task_executor.py"
WRITE_ARTIFACT = ROOT / "docs" / "reports" / "goal3507_overlay_area_prepared_payload_cache_write_pod_2026-06-05.json"
READ_ARTIFACT = ROOT / "docs" / "reports" / "goal3507_overlay_area_prepared_payload_cache_read_pod_2026-06-05.json"


class Goal3507OverlayAreaPreparedPayloadCacheTest(unittest.TestCase):
    def test_runner_exposes_prepared_payload_cache_evidence_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--payload-cache-dir",
            "--payload-cache-mode",
            "--payload-cache-evidence",
            "_write_prepared_payload_cache",
            "_read_prepared_payload_cache",
            "payload_cache_load",
            "payload_cache_write",
            "rtdl.goal3507.overlay_area_prepared_payload_cache.v1",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_cache_mode_is_off_by_default_and_read_requires_dir(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('choices=("off", "read", "write", "refresh")', text)
        self.assertIn('default="off"', text)
        self.assertIn('payload_cache_mode != "off" and payload_cache_dir is None', text)
        self.assertIn('raise ValueError("--payload-cache-mode requires --payload-cache-dir")', text)

    def test_pod_artifacts_record_write_then_read_cache_route(self) -> None:
        write_data = json.loads(WRITE_ARTIFACT.read_text(encoding="utf-8"))
        read_data = json.loads(READ_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(write_data["schema"], "rtdl.goal3507.overlay_area_prepared_payload_cache.v1")
        self.assertEqual(read_data["schema"], "rtdl.goal3507.overlay_area_prepared_payload_cache.v1")
        self.assertEqual(write_data["goal"], 3507)
        self.assertEqual(read_data["goal"], 3507)
        self.assertTrue(write_data["rtdl_commit"].startswith("19b36ccd"))
        self.assertTrue(read_data["rtdl_commit"].startswith("19b36ccd"))

        self.assertEqual(write_data["payload_cache_mode"], "refresh")
        self.assertEqual(read_data["payload_cache_mode"], "read")
        self.assertTrue(write_data["payload_cache_evidence"])
        self.assertTrue(read_data["payload_cache_evidence"])
        self.assertTrue(write_data["payload_cache_metadata"]["write_used"])
        self.assertFalse(write_data["payload_cache_metadata"]["read_used"])
        self.assertFalse(read_data["payload_cache_metadata"]["write_used"])
        self.assertTrue(read_data["payload_cache_metadata"]["read_used"])

        for side in ("left", "right"):
            with self.subTest(side=side):
                self.assertEqual(
                    read_data["payload_cache_metadata"][side]["schema"],
                    "rtdl.goal3507.overlay_area_prepared_payload_cache.v1",
                )
                self.assertGreater(read_data["payload_cache_metadata"][side]["component_count"], 0)
                self.assertGreater(read_data["payload_cache_metadata"][side]["payload_triangle_count"], 0)

        for key in (
            "relation_row_count",
            "supported_relation_row_count",
            "unsupported_relation_row_count",
            "exact_positive_row_count",
            "observed_positive_row_count",
            "left_payload_triangle_count",
            "right_payload_triangle_count",
            "tile_task_count",
            "planned_triangle_pair_count",
            "expected_triangle_pair_count",
        ):
            with self.subTest(key=key):
                self.assertEqual(write_data[key], read_data[key])

        self.assertEqual(read_data["relation_row_count"], 4543)
        self.assertEqual(read_data["supported_relation_row_count"], 2149)
        self.assertEqual(read_data["tile_task_count"], 11617)
        self.assertEqual(read_data["planned_triangle_pair_count"], 4070240)
        self.assertLess(read_data["total_area_abs_error"], 1.0e-8)
        self.assertLess(read_data["max_relation_abs_error"], 2.0e-9)
        self.assertTrue(read_data["positive_row_count_match"])

        self.assertEqual(write_data["timing_sec"]["payload_cache_load"], 0.0)
        self.assertGreater(write_data["timing_sec"]["payload_cache_write"], 1.0)
        self.assertEqual(read_data["timing_sec"]["payload_cache_write"], 0.0)
        self.assertGreater(read_data["timing_sec"]["payload_cache_load"], 0.0)
        self.assertLess(read_data["timing_sec"]["payload_cache_load"], 0.5)
        self.assertEqual(
            read_data["timing_sec"]["geometry_plus_payload_prepare"],
            read_data["timing_sec"]["payload_cache_load"],
        )

        for data in (write_data, read_data):
            for field, value in data["claim_boundary"].items():
                with self.subTest(field=field, mode=data["payload_cache_mode"]):
                    self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
