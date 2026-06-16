from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m30_librts_prepared_all_ops_refresh.py"
REPORT = ROOT / "docs/reports/goal4427_v3_0_m30_librts_prepared_all_ops_refresh_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4427_v3_0_m30_librts_prepared_all_ops_refresh_1m_1k_2026-06-16.json"
)


class Goal4427V30M30LibRtsPreparedAllOpsRefreshTest(unittest.TestCase):
    def test_runner_dry_run_records_primitive_first_all_ops_boundary(self) -> None:
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
        self.assertFalse(payload["claim_boundary"]["authors_code_comparison"])
        self.assertFalse(payload["claim_boundary"]["paper_reproduction_claim_authorized"])
        planned = {row["backend"]: row for row in payload["planned_rows"]}
        self.assertEqual(set(planned), {"embree", "optix"})
        self.assertEqual(planned["embree"]["box_count"], 1_000_000)
        self.assertEqual(planned["optix"]["query_count"], 1_000)
        self.assertGreater(planned["optix"]["repeat"], planned["embree"]["repeat"])

    def test_report_and_runner_capture_m30_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "AABB_INDEX_QUERY_2D",
            "generic_prepared_aabb_index_query_2d",
            "internal_same_contract_prepared_aabb_all_ops_refresh_not_public_speedup",
            "all_counts_match_cross_backend",
            "partner_continuation_required",
        ):
            self.assertIn(phrase, source)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "LibRTS Prepared All-Ops Refresh",
            "generic prepared AABB index all-ops",
            "1,000,000 indexed boxes",
            "repeat 240 for Embree and 3200 for OptiX",
            "does not authorize a full LibRTS paper reproduction claim",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_same_contract_all_ops_rows(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M30 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["box_count"], 1_000_000)
        self.assertEqual(payload["parameters"]["query_count"], 1_000)
        self.assertTrue(payload["comparison"]["all_counts_match_cross_backend"])
        self.assertTrue(payload["comparison"]["all_same_contract"])
        self.assertTrue(payload["comparison"]["all_primitive_first_no_partner"])
        self.assertFalse(payload["comparison"]["public_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        self.assertEqual(rows["embree"]["counts"], rows["optix"]["counts"])
        for row in rows.values():
            self.assertEqual(row["generic_primitive"], "AABB_INDEX_QUERY_2D")
            self.assertEqual(row["primitive_contract"], "generic_prepared_aabb_index_query_2d")
            self.assertTrue(row["cpu_reference_skipped"])
            self.assertFalse(row["native_engine_customization"])
            self.assertFalse(row["partner_continuation_required"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertGreater(row["query_total_sec"], 1.0)
        pair = payload["comparison"]["same_contract_backend_pair"]
        self.assertTrue(pair["same_contract"])
        self.assertTrue(pair["same_counts"])
        self.assertTrue(pair["same_dataset"])
        self.assertGreater(pair["embree_over_optix_query_median"], 1.0)


if __name__ == "__main__":
    unittest.main()
