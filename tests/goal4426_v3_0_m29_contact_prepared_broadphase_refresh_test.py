from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m29_contact_prepared_broadphase_refresh.py"
REPORT = ROOT / "docs/reports/goal4426_v3_0_m29_contact_prepared_broadphase_refresh_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4426_v3_0_m29_contact_prepared_broadphase_refresh_grid65536_2026-06-16.json"
)


class Goal4426V30M29ContactPreparedBroadphaseRefreshTest(unittest.TestCase):
    def test_runner_dry_run_records_primitive_only_contact_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output",
                    str(output),
                ],
                cwd=str(ROOT),
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "dry_run")
        self.assertTrue(payload["claim_boundary"]["primitive_first_no_partner_needed"])
        self.assertFalse(payload["claim_boundary"]["partner_continuation_required"])
        self.assertFalse(payload["claim_boundary"]["full_contact_manifold_solver_claim_authorized"])
        planned = {row["backend"]: row for row in payload["planned_rows"]}
        self.assertEqual(set(planned), {"embree", "optix"})
        self.assertEqual(planned["embree"]["grid_count"], 65_536)
        self.assertEqual(planned["optix"]["witness_capacity"], 65_536)
        self.assertGreaterEqual(planned["embree"]["repeat"], 20)
        self.assertEqual(planned["embree"]["repeat"], planned["optix"]["repeat"])

    def test_report_and_runner_capture_m29_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "AABB_INDEX_QUERY_2D",
            "generic_aabb_intersection_pair_rows_2d",
            "primitive_first_no_partner_needed",
            "internal_same_contract_prepared_broadphase_refresh_not_public_speedup",
            "full_contact_manifold_solver_claim_authorized",
            "candidate_compactness",
        ):
            self.assertIn(phrase, source)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Contact Prepared Broadphase Refresh",
            "same app-agnostic candidate-discovery contract",
            "jittered_grid_65536",
            "4,294,967,296 possible all-pairs checks",
            "does not authorize a public full contact-manifold solver claim",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_same_contract_prepared_broadphase_rows(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M29 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["grid_count"], 65_536)
        self.assertTrue(payload["comparison"]["all_match_cpu_reference"])
        self.assertTrue(payload["comparison"]["all_complete_candidate_coverage"])
        self.assertTrue(payload["comparison"]["all_non_overflowed"])
        self.assertTrue(payload["comparison"]["no_partner_continuation_required"])
        self.assertFalse(payload["comparison"]["public_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        for row in rows.values():
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertFalse(row["overflowed"])
            self.assertEqual(row["candidate_discovery_primitive"], "AABB_INDEX_QUERY_2D")
            self.assertEqual(row["candidate_discovery_contract"], "generic_aabb_intersection_pair_rows_2d")
            self.assertEqual(row["primitive_under_test"], "COLLECT_K_BOUNDED")
            self.assertEqual(row["aabb_candidate_pair_count"], 65_536)
            self.assertEqual(row["valid_count"], 65_536)
            self.assertGreater(row["all_pairs_per_candidate"], 1_000)
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(row["claim_boundary"]["full_contact_manifold_solver_claim_authorized"])
        pair = payload["comparison"]["same_contract_backend_pair"]
        self.assertTrue(pair["same_contract"])
        self.assertTrue(pair["same_dataset"])
        self.assertTrue(pair["same_candidate_count"])
        self.assertTrue(pair["both_match_cpu_reference"])


if __name__ == "__main__":
    unittest.main()
