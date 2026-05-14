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
REPORT = ROOT / "docs" / "reports" / "goal1987_database_partner_columnar_reductions_2026-05-14.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal1987_pod_database_partner_columnar_reductions_cupy_perf.json"
PREFLIGHT = ROOT / "scripts" / "goal1908_v2_local_preflight.py"


class Goal1987DatabasePartnerColumnarReductionsTest(unittest.TestCase):
    def test_partner_adapters_expose_generic_columnar_predicate_reductions(self) -> None:
        adapters = ADAPTERS.read_text(encoding="utf-8")
        init_text = INIT.read_text(encoding="utf-8")

        self.assertIn("def columnar_rows_to_partner_columns", adapters)
        self.assertIn("def columnar_payload_to_partner_columns", adapters)
        self.assertIn("def partner_columnar_predicate_mask", adapters)
        self.assertIn("def partner_columnar_predicate_reduce", adapters)
        self.assertIn("def partner_columnar_predicate_reduce_batch", adapters)
        self.assertIn("shared_predicate_mask_count", adapters)
        self.assertIn("generic_columnar_payload_columns", adapters)
        self.assertIn("caller_supplied_columnar_payload", adapters)
        self.assertIn("native_engine_row_contract", adapters)
        self.assertIn("not_called_partner_reference_only", adapters)
        self.assertIn("from .partner_adapters import columnar_rows_to_partner_columns", init_text)
        self.assertIn("from .partner_adapters import columnar_payload_to_partner_columns", init_text)
        self.assertIn('"partner_columnar_predicate_reduce"', init_text)
        self.assertIn('"partner_columnar_predicate_reduce_batch"', init_text)

    def test_database_control_path_uses_generic_partner_columnar_reductions(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("_database_partner_columnar_continuation", text)
        self.assertIn("columnar_payload_to_partner_columns", text)
        self.assertIn("partner_columnar_predicate_reduce_batch", text)
        self.assertIn('"partner_columnar_predicate_reduce_batch"', text)
        self.assertIn("v2 uses Python+partner continuations+RTDL", text)

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

    def test_report_preflight_and_pod_artifact_record_design_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        preflight = PREFLIGHT.read_text(encoding="utf-8")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("reusable partner algebra", report)
        self.assertIn("2.755x", report)
        self.assertIn("slower than the old fused app-local kernel", report)
        self.assertIn("tests.goal1987_database_partner_columnar_reductions_test", preflight)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["claim_boundary"]["reusable_partner_columnar_reductions"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])
        self.assertTrue(payload["claim_boundary"]["rawkernel_faster_than_generic_currently"])
        rows = {row["copies"]: row for row in payload["results"]}
        self.assertTrue(rows[1000]["matches_rawkernel"])
        self.assertGreater(rows[100000]["columnar_vs_rawkernel_ratio"], 2.0)


if __name__ == "__main__":
    unittest.main()
