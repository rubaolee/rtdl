from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m28_raydb_prepared_grouped_refresh.py"
REPORT = ROOT / "docs/reports/goal4425_v3_0_m28_raydb_prepared_grouped_refresh_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4425_v3_0_m28_raydb_prepared_grouped_refresh_262144_2026-06-16.json"
)


class Goal4425V30M28RaydbPreparedGroupedRefreshTest(unittest.TestCase):
    def test_runner_dry_run_records_primitive_first_matrix(self) -> None:
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
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        planned = {(row["backend"], row["mode"]): row for row in payload["planned_rows"]}
        self.assertEqual(set(planned), {("embree", "count"), ("embree", "sum"), ("optix", "count"), ("optix", "sum")})
        self.assertGreaterEqual(planned[("optix", "count")]["repeat"], 1000)
        self.assertLess(planned[("embree", "sum")]["repeat"], planned[("embree", "count")]["repeat"])

    def test_report_and_runner_capture_m28_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "paper_rt_embree",
            "paper_rt_optix_prepared_grouped_reduction",
            "primitive_first_no_partner_needed",
            "same_contract_prepared_query_refresh_not_public_speedup",
            "prepared_primitive_payload_reused",
            "v2_5_selected_path",
        ):
            self.assertIn(phrase, source)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "RayDB Prepared Grouped-Reduction Refresh",
            "primitive-first",
            "Does this app need a partner for count/sum? | No.",
            "goal4425_v3_0_m28_raydb_prepared_grouped_refresh_262144_2026-06-16.json",
            "13.78x",
            "121.05x",
            "do not authorize release wording",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_same_contract_primitive_first_rows(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M28 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["generated_rows"], 262_144)
        self.assertEqual(payload["parameters"]["generated_groups"], 1024)
        self.assertTrue(payload["comparison"]["all_match_cpu_reference"])
        self.assertTrue(payload["comparison"]["no_partner_continuation_required"])
        self.assertTrue(payload["comparison"]["all_prepared_steady_state"])
        self.assertFalse(payload["comparison"]["public_speedup_claim_authorized"])
        rows = {(row["backend"], row["mode"]): row for row in payload["rows"]}
        self.assertEqual(set(rows), {("embree", "count"), ("embree", "sum"), ("optix", "count"), ("optix", "sum")})
        for row in rows.values():
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["prepared_primitive_payload_reused"])
            self.assertTrue(row["prepared_ray_batch_reused"])
            self.assertEqual(row["v2_5_selected_path"], "prepared_fused_generic_grouped_reduction")
            self.assertFalse(row["partner_continuation_required"])
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertEqual(len(payload["comparison"]["same_contract_backend_pairs"]), 2)
        self.assertTrue(
            all(pair["same_contract"] and pair["both_match_cpu_reference"] for pair in payload["comparison"]["same_contract_backend_pairs"])
        )


if __name__ == "__main__":
    unittest.main()
