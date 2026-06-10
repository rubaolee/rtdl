from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4266_large_scale_partner_comparison.py"
ADAPTER = ROOT / "src" / "rtdsl" / "v2_8_segmented_typed_stream_adapter.py"


class Goal4266LargeScalePartnerComparisonTest(unittest.TestCase):
    def test_dry_run_declares_large_scale_contracts_and_time_floor(self) -> None:
        output = ROOT / "scratch" / "goal4266_test_dry_run.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--target-hot-total-sec",
                "1.25",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertIn("[goal4266] wrote", completed.stdout)
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal4266.large_scale_cupy_numba_partner_comparison.v1")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(tuple(payload["partners"]), ("cupy", "numba"))
        self.assertGreaterEqual(float(payload["target_hot_total_sec"]), 1.0)
        grouped = payload["contracts"]["raydb_style_unfused_grouped_reductions"]
        self.assertIn("segmented_count_i64", grouped["operations"])
        self.assertIn("segmented_sum_f64", grouped["operations"])
        self.assertIn("segmented_min_f64", grouped["operations"])
        self.assertIn("segmented_max_f64", grouped["operations"])
        self.assertIn("avg_as_sum_count", grouped["derived"])
        compact = payload["contracts"]["triangle_candidate_row_compaction"]
        self.assertEqual(tuple(compact["operations"]), ("compact_mask_i64",))
        self.assertFalse(payload["claim_boundary"]["partner_winner_claim_authorized"])

    def test_front_door_metadata_does_not_materialize_adapter_like_for_lengths(self) -> None:
        source = ADAPTER.read_text(encoding="utf-8")
        self.assertNotIn("len(_adapter_like(", source)
        self.assertIn("_partner_column_length(mapped_columns[\"group_ids\"])", source)
        self.assertIn("_partner_column_length(values)", source)


if __name__ == "__main__":
    unittest.main()
