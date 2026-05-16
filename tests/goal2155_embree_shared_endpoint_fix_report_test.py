from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2155_embree_shared_endpoint_segment_intersection_fix_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2155_rayjoin_external_cdb_warm_after_embree_endpoint_fix_pod_2026-05-16.json"


class Goal2155EmbreeSharedEndpointFixReportTest(unittest.TestCase):
    def test_report_records_root_cause_fix_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "This is not RayJoin app customization",
            "CPU minus Embree: 957 rows",
            "shared-endpoint index",
            "Goal2155 resolves the same-contract mismatch",
            "Clean RTDL commit on pod: `9931585362e0e27ccf1a4e657afc7fd670209041`",
            "full RayJoin paper reproduction",
            "v2.0 release authorization",
            "External review is still needed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_artifact_confirms_all_goal2155_warm_rows_pass_parity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["commit"], "9931585362e0e27ccf1a4e657afc7fd670209041")
        self.assertFalse(payload["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])

        for label, case in payload["cases"].items():
            for backend, row in case["backends"].items():
                with self.subTest(label=label, backend=backend):
                    self.assertEqual(row["status"], "ok")
                    self.assertTrue(row["row_count_consistent"])
                    self.assertTrue(row["all_parity_vs_cpu_python_reference"])

        self.assertEqual(
            payload["cases"]["lsi_county64_self_positive_control"]["backends"]["embree"]["row_counts"],
            [4766, 4766, 4766],
        )


if __name__ == "__main__":
    unittest.main()
