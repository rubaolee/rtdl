import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1722_goal1660_manifest_reality_correction_after_v1_0_pod_adapter_2026-05-12.md"
MATRIX_JSON = ROOT / "docs" / "reports" / "goal1660_v1_6_11_vs_v1_0_perf_matrix_2026-05-10.json"


class Goal1722Goal1660ManifestRealityCorrectionTest(unittest.TestCase):
    def test_report_records_fail_closed_manifest_correction(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("accept-with-boundary", text)
        self.assertIn("current_only_v1_0_missing_engine_selector", text)
        self.assertIn("planned=16", text)
        self.assertIn("does not claim a public speedup", text)

    def test_manifest_matches_goal1720_pod_observed_command_support(self) -> None:
        payload = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["planned_row_count"], 16)
        self.assertEqual(payload["blocked_or_excluded_row_count"], 20)
        statuses: dict[str, int] = {}
        for row in payload["rows"]:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        self.assertEqual(statuses["planned"], 16)
        self.assertEqual(statuses["current_only_v1_0_missing_engine_selector"], 12)
        self.assertEqual(statuses["excluded"], 7)
        self.assertEqual(statuses["shared_primitive_alias"], 1)

    def test_legacy_optix_adaptations_do_not_keep_unsupported_backend_flag(self) -> None:
        payload = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
        adapted = [
            row for row in payload["rows"]
            if row.get("v1_0_command_shape") == "legacy_optix_only_without_backend_selector"
        ]
        self.assertEqual(len(adapted), 12)
        for row in adapted:
            with self.subTest(app=row["app"]):
                self.assertEqual(row["engine"], "optix")
                self.assertEqual(row["status"], "planned")
                self.assertTrue(row["compare_v1_0"])
                self.assertNotIn("--backend", row["v1_0_command"])


if __name__ == "__main__":
    unittest.main()
