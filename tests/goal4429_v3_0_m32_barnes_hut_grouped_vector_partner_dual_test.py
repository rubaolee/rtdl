from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_0_m32_barnes_hut_grouped_vector_partner_dual.py"
REPORT = ROOT / "docs/reports/goal4429_v3_0_m32_barnes_hut_grouped_vector_partner_dual_2026-06-16.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4429_v3_0_m32_barnes_hut_grouped_vector_partner_dual_262144x8_2026-06-16.json"
)


class Goal4429V30M32BarnesHutGroupedVectorPartnerDualTest(unittest.TestCase):
    def test_barnes_hut_descriptor_promotes_numba_as_no_cpp_reference_partner(self) -> None:
        from examples.benchmark_apps.barnes_hut import (
            rtdl_barnes_hut_benchmark_app as barnes_hut,
        )

        descriptor = barnes_hut.describe_barnes_hut_grouped_vector_sum_typed_stream(partner="numba")
        self.assertEqual(descriptor["execution_path"], "generic_grouped_vector_sum_typed_stream_partner_columns")
        self.assertEqual(descriptor["operation"], "grouped_vector_sum_f64x2")
        self.assertIn("numba", descriptor["partner_policy"]["supported_partners"])
        self.assertEqual(
            descriptor["partner_policy"]["numba_status"],
            "preview_supported_no_cpp_reference_for_grouped_vector_sum_f64x2",
        )
        self.assertTrue(descriptor["partner_policy"]["numba_reference_partner_supported"])
        self.assertFalse(descriptor["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(descriptor["claim_boundary"]["public_speedup_claim_authorized"])

    def test_runner_dry_run_records_dual_partner_contract_without_cuda(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--group-count",
                    "1024",
                    "--rows-per-group",
                    "4",
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
        self.assertTrue(payload["claim_boundary"]["partner_continuation_required"])
        self.assertTrue(payload["claim_boundary"]["best_partner_plus_numba_reference_required"])
        self.assertFalse(payload["claim_boundary"]["native_rt_traversal_executed"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        planned = {row["partner"]: row for row in payload["planned_rows"]}
        self.assertEqual(set(planned), {"cupy", "numba"})
        self.assertEqual(planned["cupy"]["row_count"], 4096)
        policies = {row["partner"]: row for row in payload["descriptor_policy"]}
        self.assertIn("numba", policies["cupy"]["supported_partners"])
        self.assertTrue(policies["numba"]["numba_reference_partner_supported"])

    def test_report_and_runner_capture_m32_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "generic_grouped_vector_sum_typed_stream_partner_columns",
            "best_partner_plus_numba_reference_required",
            "caller_supplied_partner_columns_no_hidden_host_rows",
            "all_front_doors_report_no_hidden_host_rows",
            "rt_core_speedup_claim_authorized",
        ):
            self.assertIn(phrase, source)

        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Barnes-Hut Grouped Vector Partner-Dual Refresh",
            "CuPy",
            "Numba",
            "caller-supplied partner-owned columns",
            "does not execute native RT traversal",
            "does not authorize public speedup wording",
        ):
            self.assertIn(phrase, report)

    def test_pod_evidence_records_cupy_and_numba_same_front_door(self) -> None:
        self.assertTrue(EVIDENCE_JSON.exists(), f"missing M32 pod evidence: {EVIDENCE_JSON}")
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["parameters"]["group_count"], 262_144)
        self.assertEqual(payload["parameters"]["rows_per_group"], 8)
        self.assertEqual(payload["parameters"]["row_count"], 2_097_152)
        self.assertFalse(payload["claim_boundary"]["native_rt_traversal_executed"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        comparison = payload["comparison"]
        self.assertTrue(comparison["all_outputs_match_reference_with_tolerance"])
        self.assertTrue(comparison["signatures_match_between_cupy_and_numba"])
        self.assertTrue(comparison["all_front_doors_report_no_hidden_host_rows"])
        self.assertTrue(comparison["all_presegmented_offsets_used"])
        self.assertTrue(comparison["all_global_atomic_add_avoided"])
        self.assertFalse(comparison["public_speedup_claim_authorized"])
        rows = {row["partner"]: row for row in payload["rows"]}
        self.assertEqual(set(rows), {"cupy", "numba"})
        for row in rows.values():
            self.assertEqual(row["execution_path"], "generic_grouped_vector_sum_typed_stream_partner_columns")
            self.assertEqual(row["operation"], "grouped_vector_sum_f64x2")
            self.assertEqual(row["source_materialization"], "caller_supplied_partner_columns_no_hidden_host_rows")
            self.assertTrue(row["matches_reference_tolerance"])
            self.assertLessEqual(row["max_abs_diff_x"], row["reference_tolerance_abs"])
            self.assertLessEqual(row["max_abs_diff_y"], row["reference_tolerance_abs"])
            self.assertTrue(row["partner_metadata_presegmented_offsets_used"])
            self.assertFalse(row["partner_metadata_global_atomic_add_used"])
            self.assertGreater(row["timed_total_sec"], 0.1)
            self.assertFalse(row["claim_boundary"]["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
