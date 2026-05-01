import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal884_segment_polygon_native_gate_local_precloud_2026-04-24.md"
NON_STRICT = ROOT / "docs" / "reports" / "goal884_segment_polygon_gate_local_non_strict_2026-04-24.json"
STRICT = ROOT / "docs" / "reports" / "goal884_segment_polygon_gate_local_strict_2026-04-24.json"
PRECLOUD = ROOT / "docs" / "reports" / "goal884_pre_cloud_readiness_after_goal879_883_2026-04-24.json"


class Goal884SegmentPolygonPrecloudGateReportTest(unittest.TestCase):
    def test_report_preserves_local_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("local pre-cloud readiness artifact", text)
        self.assertIn("not a segment/polygon promotion claim", text)
        self.assertIn("not a speedup claim", text)
        self.assertIn("Do not restart the pod per app", text)

    def test_local_gate_artifacts_record_expected_optix_unavailability(self) -> None:
        non_strict = json.loads(NON_STRICT.read_text(encoding="utf-8"))
        strict = json.loads(STRICT.read_text(encoding="utf-8"))

        self.assertEqual(non_strict["status"], "non_strict_recorded_gaps")
        self.assertEqual(strict["status"], "fail")
        self.assertIn("optix_host_indexed did not run", strict["strict_failures"])
        self.assertIn("optix_native did not run", strict["strict_failures"])

        for payload in (non_strict, strict):
            cpu = next(record for record in payload["records"] if record["label"] == "cpu_python_reference")
            self.assertEqual(cpu["status"], "ok")
            for label in ("optix_host_indexed", "optix_native"):
                record = next(item for item in payload["records"] if item["label"] == label)
                self.assertEqual(record["error_type"], "FileNotFoundError")
                self.assertIn("librtdl_optix not found", record["error"])

    def test_pre_cloud_gate_remains_valid(self) -> None:
        payload = json.loads(PRECLOUD.read_text(encoding="utf-8"))
        self.assertTrue(payload["valid"], payload.get("invalid_checks"))
        self.assertIn("does not start cloud", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
