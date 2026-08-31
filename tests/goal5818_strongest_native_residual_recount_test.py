from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


class Goal5818StrongestNativeResidualRecountTest(unittest.TestCase):
    def test_offline_recount_matches_frozen_result(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/goal5818_strongest_native_residual_recount.py")],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        observed = json.loads(completed.stdout)
        frozen = json.loads(
            (
                ROOT
                / "history/internal_docs/goal5818_strongest_native_residual_recount_20260829.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(observed, frozen)
        self.assertEqual(observed["existing_native_execution"]["native_collision_count"], 0)
        self.assertEqual(observed["existing_native_execution"]["residual_survival_count"], 5)
        self.assertFalse(observed["cp002_exact_dataflow"]["closest_hit_in_path"])
        self.assertFalse(
            observed["cp002_exact_dataflow"]["payload_read_or_write_in_is_ah_path"]
        )

    def test_claim_routing_is_honestly_outcome_known(self) -> None:
        routing = json.loads(
            (
                ROOT / "history/internal_docs/goal5818_claim_branches_20260829.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(routing["epistemic_status"]["scientific_preregistration_claimed"])
        self.assertEqual(routing["selected_branch_after_offline_recount"], "A")
        self.assertIn("A", routing["branches"])
        self.assertIn("B", routing["branches"])
        self.assertIn("C", routing["branches"])
        self.assertIn("D", routing["branches"])


if __name__ == "__main__":
    unittest.main()
