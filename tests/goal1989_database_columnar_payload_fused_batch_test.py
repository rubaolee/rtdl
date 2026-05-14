from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "src" / "rtdsl" / "partner_adapters.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
EXAMPLE = ROOT / "examples" / "rtdl_control_apps_cupy_rawkernel.py"
REPORT = ROOT / "docs" / "reports" / "goal1989_database_columnar_payload_fused_batch_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1989_pod_database_partner_columnar_fused_batch_cupy_perf.json"


class Goal1989DatabaseColumnarPayloadFusedBatchTest(unittest.TestCase):
    def test_partner_adapter_exposes_columnar_payload_and_fused_batch_contract(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def columnar_payload_to_partner_columns", adapters)
        self.assertIn("caller_supplied_columnar_payload", adapters)
        self.assertIn("def partner_columnar_predicate_reduce_batch", adapters)
        self.assertIn("_cupy_columnar_predicate_reduce_batch_fused", adapters)
        self.assertIn("cupy_fused_rawkernel_from_generic_summary_specs", adapters)
        self.assertIn("output_dtype", adapters)
        self.assertIn("from .partner_adapters import columnar_payload_to_partner_columns", init_text)
        self.assertIn('"columnar_payload_to_partner_columns"', init_text)

    def test_database_v2_path_uses_generic_columnar_payload_fused_batch(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("columnar_payload_to_partner_columns", text)
        self.assertIn("partner_columnar_predicate_reduce_batch", text)
        self.assertIn('"partner_columnar_predicate_reduce_batch"', text)
        self.assertIn('"output_dtype": "int32"', text)
        self.assertNotIn("partner_columnar_predicate_reductions", text)

    def test_cpu_fallback_still_matches_oracle(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--app",
                "database_analytics",
                "--copies",
                "4",
                "--partner",
                "cpu_fallback",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn('"matches_v1_8_python_rtdl_oracle": true', completed.stdout)

    def test_report_and_pod_artifact_record_parity_without_release_overclaim(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("columnar payload handoff + fused batch summaries", report)
        self.assertIn("approximately parity", report)
        self.assertIn("does not customize the RTDL native engine", report)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["reusable_partner_columnar_payload_handoff"])
        self.assertTrue(payload["claim_boundary"]["cupy_fused_rawkernel_generated_from_generic_summary_specs"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertTrue(rows[100000]["all_match_rawkernel"])
        self.assertLess(rows[100000]["fused_columnar_payload_vs_rawkernel_ratio"], 1.05)


if __name__ == "__main__":
    unittest.main()
