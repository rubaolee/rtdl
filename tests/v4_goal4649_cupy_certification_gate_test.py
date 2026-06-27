from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4
from rtdsl import v4_cupy_certification as gate


SCRIPT = ROOT / "scripts" / "v4_goal4649_cupy_grouped_reduction_certification_gate.py"


class V4Goal4649CuPyCertificationGateTest(unittest.TestCase):
    def test_target_matrix_separates_ready_from_mapping_debt(self) -> None:
        targets = gate.v4_goal4649_cupy_certification_targets()
        by_id = {row["candidate_id"]: row for row in targets}

        self.assertEqual(4, len(targets))
        self.assertEqual(
            gate.V4_GOAL4649_CUPY_READY_FOR_POD,
            by_id["cupy_grouped_reduction_device_columns_262144"]["gate_status"],
        )
        self.assertEqual(
            gate.V4_GOAL4649_CUPY_READY_FOR_POD,
            by_id["cupy_grouped_reduction_device_columns_524288"]["gate_status"],
        )
        self.assertEqual(
            gate.V4_GOAL4649_CUPY_REQUIRES_MAPPING,
            by_id["cupy_segment_polygon_hitcount_prepared_scaling"]["gate_status"],
        )
        self.assertEqual(
            gate.V4_GOAL4649_CUPY_REQUIRES_MAPPING,
            by_id["cupy_hausdorff_witness_continuation"]["gate_status"],
        )

    def test_ready_targets_have_frozen_bars_and_no_public_claims(self) -> None:
        ready = gate.v4_goal4649_ready_cupy_targets()

        self.assertEqual(2, len(ready))
        for row in ready:
            self.assertEqual("grouped_vector_sum_f64x2", row["operator"])
            self.assertEqual(1.0, row["correctness_parity_required"])
            self.assertEqual(1.20, row["representative_speedup_floor"])
            self.assertEqual(0.98, row["partner_parity_floor"])
            self.assertEqual(3, row["warmup"])
            self.assertEqual(100, row["repeat"])
            self.assertFalse(row["public_claim_authorized"])
            self.assertFalse(row["partner_migration_counts_as_v4_speed_win"])
            self.assertFalse(row["partner_parity_counts_as_v4_speed_win"])
            self.assertIn("partner='cupy'", row["v4_frontdoor_route"])

    def test_frontdoor_exports_goal4649_target_helpers(self) -> None:
        self.assertEqual(gate.V4_GOAL4649_CUPY_CERTIFICATION_STATUS, v4.V4_GOAL4649_CUPY_CERTIFICATION_STATUS)
        self.assertEqual(2, len(v4.v4_goal4649_ready_cupy_targets()))
        target = v4.v4_goal4649_target_by_id("cupy_grouped_reduction_device_columns_262144")
        self.assertEqual(262144, target["representative_rows"])
        with self.assertRaisesRegex(ValueError, "unknown Goal4649 CuPy candidate"):
            v4.v4_goal4649_target_by_id("barnes_hut_aggregate_tree_numba_cuda_fused")

    def test_gate_script_dry_run_writes_non_authorizing_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "dryrun.json"
            md_out = Path(tmp) / "dryrun.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual("goal4649_cupy_gate_dry_run_no_claims", payload["status"])
            self.assertFalse(payload["cupy_performance_claim_authorized"])
            self.assertFalse(payload["pod_spend_authorized_by_this_file"])
            self.assertEqual(2, len(payload["ready_targets"]))
            self.assertIn("CuPy performance remains unauthorized", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
