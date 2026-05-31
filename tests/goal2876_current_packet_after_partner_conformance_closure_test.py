from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs/reports/goal2876_current_packet_after_conformance_pod"
REPORT = ROOT / "docs/reports/goal2876_current_packet_after_partner_conformance_closure_2026-05-31.md"


class Goal2876CurrentPacketAfterPartnerConformanceClosureTest(unittest.TestCase):
    def test_current_packet_summary_passes_with_clean_source_and_boundaries(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertTrue(summary["returncode_ok"])
        self.assertTrue(summary["artifact_status_ok"])
        self.assertTrue(summary["source_commit_consistent"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual([], summary["runner_metadata"]["source_dirty"])
        self.assertIn("NVIDIA RTX A5000", summary["runner_metadata"]["gpu"])

    def test_all_child_artifacts_are_clean_passes_on_same_commit(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))
        expected_commit = summary["source_commit"]

        for artifact_name, metadata in summary["artifacts"].items():
            payload = json.loads((ARTIFACT_DIR / artifact_name).read_text(encoding="utf-8"))
            self.assertEqual("pass", payload["status"], artifact_name)
            self.assertEqual(expected_commit, payload["source_commit"], artifact_name)
            self.assertEqual([], payload["source_dirty"], artifact_name)
            self.assertIn("NVIDIA RTX A5000", payload["gpu"], artifact_name)
            boundary = payload.get("claim_boundary", {})
            for key, value in boundary.items():
                if key.endswith("_claim_authorized") or key == "native_engine_customization":
                    self.assertFalse(value, f"{artifact_name} boundary {key}")

    def test_readiness_packet_uses_goal2876_runner_summary(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "docs/reports/goal2876_current_packet_after_conformance_pod/goal2855_summary.json",
            packet["current_canonical_runner"]["summary_path"],
        )
        self.assertEqual("pass", packet["current_canonical_runner"]["status"])
        self.assertTrue(packet["required_report_presence"][
            "docs/reports/goal2876_current_packet_after_partner_conformance_closure_2026-05-31.md"
        ])

    def test_report_records_self_dirty_retry_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2876",
            "self-dirty",
            "all_pass: true",
            "NVIDIA RTX A5000",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
