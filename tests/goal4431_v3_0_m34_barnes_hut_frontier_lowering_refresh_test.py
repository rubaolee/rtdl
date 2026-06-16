from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m34_barnes_hut_frontier_lowering_refresh.py"
REPORT = ROOT / "docs/reports/goal4431_v3_0_m34_barnes_hut_frontier_lowering_refresh_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4431_v3_0_m34_barnes_hut_frontier_lowering_refresh_8192_2026-06-16.json"
)


class Goal4431V30M34BarnesHutFrontierLoweringRefreshTest(unittest.TestCase):
    def test_runner_dry_run_records_host_materialized_boundary(self) -> None:
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
        self.assertEqual(payload["planned"]["same_contract"], "generic_aggregate_frontier_collect_2d_v1")
        self.assertEqual(set(payload["planned"]["backends"]), {"embree", "optix"})
        self.assertTrue(payload["claim_boundary"]["host_materialized_frontier_rows"])
        self.assertFalse(payload["claim_boundary"]["device_resident_partner_handoff_proven"])
        self.assertFalse(payload["claim_boundary"]["clean_device_continuation_claim_authorized"])

    def test_runner_uses_m8_native_lowering_not_app_specific_engine(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("run_v3_m8_aggregate_frontier_lowering_case", text)
        self.assertIn("generic_aggregate_frontier_collect_2d_v1", text)
        self.assertIn("host_materialized_frontier_rows", text)
        self.assertNotIn("barnes_hut_force_kernel", text)
        self.assertNotIn("app_specific_native", text)

    def test_report_records_boundary_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "host-materialized frontier rows",
            "not yet a clean device-resident producer",
            "same-stream partner grouped-vector",
            "not evidence that RT cores cannot help Barnes-Hut",
            "device-resident aggregate-frontier column producer",
        ):
            self.assertIn(phrase, text)

    def test_pod_evidence_records_same_contract_rows_and_bridge_debt(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M34 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        comparison = payload["comparison"]
        self.assertEqual(set(comparison["same_contract_backends"]), {"embree", "optix"})
        self.assertEqual(comparison["same_contract"], "generic_aggregate_frontier_collect_2d_v1")
        self.assertTrue(comparison["all_rows_match_reference"])
        self.assertTrue(comparison["all_native_engine_app_specific_false"])
        self.assertGreater(comparison["frontier_row_count"], 1_000_000)
        self.assertTrue(comparison["host_materialized_frontier_rows"])
        self.assertFalse(comparison["device_resident_partner_handoff_proven"])
        self.assertFalse(comparison["clean_device_continuation_claim_authorized"])
        self.assertFalse(comparison["rt_core_speedup_claim_authorized"])
        rows = {row["backend"]: row for row in payload["m8_payload"]["backend_rows"]}
        self.assertEqual(set(rows), {"embree", "optix"})
        self.assertEqual(rows["embree"]["frontier_row_count"], rows["optix"]["frontier_row_count"])
        self.assertGreater(rows["embree"]["median_seconds"], 0.0)
        self.assertGreater(rows["optix"]["median_seconds"], 0.0)


if __name__ == "__main__":
    unittest.main()
