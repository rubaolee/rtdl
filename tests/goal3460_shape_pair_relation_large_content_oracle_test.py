from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3460_shape_pair_relation_large_content_oracle.py"
REPORT = ROOT / "docs" / "reports" / "goal3460_shape_pair_relation_large_content_oracle_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3460_shape_pair_relation_large_content_oracle_pod_2026-06-05.json"


class Goal3460ShapePairRelationLargeContentOracleTest(unittest.TestCase):
    def test_script_defines_independent_large_content_oracle(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "rtdl.goal3460.shape_pair_relation_large_content_oracle.v1",
            "_host_oracle_rows",
            "_device_rows",
            "_diff_rows",
            "ctypes.c_float",
            "requires_segment_intersection",
            "requires_point_containment",
            "left_ordinal",
            "right_ordinal",
            "bbox_candidate_count",
            "progress_every",
        ):
            self.assertIn(phrase, script)

    def test_script_mirrors_native_relation_semantics(self) -> None:
        script = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "abs(denom) < 1.0e-7",
            "0.0 <= t <= 1.0",
            "0.0 <= u <= 1.0",
            "_point_in_polygon_inclusive",
            "_containment_required",
            "if not requires_segment",
        ):
            self.assertIn(phrase, script)

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3460",
            "independent large-scale content oracle",
            "float32 coordinate quantization",
            "non-integer and non-orthogonal",
            "does not authorize",
            "not an exact overlay-area completion",
            "generic polygon-continuation primitive",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3460 pod artifact pending")
    def test_pod_artifact_records_large_content_match(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3460.shape_pair_relation_large_content_oracle.v1")
        self.assertEqual(payload["goal"], 3460)
        self.assertTrue(payload["rows_match"])
        self.assertEqual(payload["host_oracle_row_count"], payload["device_row_count"])
        self.assertGreater(payload["host_oracle_row_count"], 0)
        self.assertEqual(payload["diff"]["missing_pair_count"], 0)
        self.assertEqual(payload["diff"]["extra_pair_count"], 0)
        self.assertEqual(payload["diff"]["flag_mismatch_count"], 0)
        self.assertEqual(payload["metadata_schema_id"], "shape_pair_relation_flags_2d_device_columns")
        self.assertTrue(payload["metadata_geometry_payload_device_resident"])
        self.assertTrue(payload["metadata_ordinal_columns_device_resident"])
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
