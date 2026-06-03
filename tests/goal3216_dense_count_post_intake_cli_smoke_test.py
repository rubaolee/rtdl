from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3216_dense_count_post_intake_cli_smoke_2026-06-03.json"
REPORT = ROOT / "docs" / "reports" / "goal3216_dense_count_post_intake_cli_smoke_2026-06-03.md"


class Goal3216DenseCountPostIntakeCliSmokeTest(unittest.TestCase):
    def test_post_intake_pod_smoke_executes_dense_count_route(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["execution_route"], "prepared_optix_left_id_dense_count_reuse")
        self.assertEqual(
            data["summary"]["output_contract"],
            "segment_segment_intersection_count_by_left_id_dense_device_column",
        )
        dense = data["dense_left_id_count_columns"]
        self.assertTrue(dense["device_resident"])
        self.assertEqual(dense["native_symbol"], "rtdl_optix_prepared_segment_pair_left_id_count_device_columns")
        self.assertEqual(dense["source_row_count"], data["row_count"])
        self.assertFalse(dense["overflow"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertNotIn("rows", data)

    def test_report_keeps_smoke_separate_from_perf_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "rebuilt `librtdl_optix.so` from commit `a9277a1f`",
            "smoke test, not a timing claim",
            "must not be used as steady-state performance evidence",
            "does not authorize release",
        ):
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()
