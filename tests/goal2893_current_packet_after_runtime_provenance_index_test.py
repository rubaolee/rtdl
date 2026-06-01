from pathlib import Path
import json
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs/reports/goal2893_current_packet_after_runtime_provenance_index_pod"
REPORT = ROOT / "docs/reports/goal2893_current_packet_after_runtime_provenance_index_2026-05-31.md"
EXPECTED_COMMIT = "e6bf7f85cb8a32e5cd5c32210f192a15207e2184"


class Goal2893CurrentPacketAfterRuntimeProvenanceIndexTest(unittest.TestCase):
    def test_current_packet_summary_passes_with_clean_source_and_boundaries(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", summary["status"])
        self.assertTrue(summary["all_pass"])
        self.assertEqual(EXPECTED_COMMIT, summary["source_commit"])
        self.assertEqual(7, summary["artifact_count"])
        self.assertEqual(7, summary["expected_artifact_count"])
        self.assertTrue(summary["returncode_ok"])
        self.assertTrue(summary["artifact_status_ok"])
        self.assertTrue(summary["source_commit_consistent"])
        self.assertEqual({}, summary["dirty_artifacts"])
        self.assertEqual({}, summary["claim_boundary_violations"])
        self.assertEqual([], summary["runner_metadata"]["source_dirty"])
        self.assertIn("NVIDIA RTX A5000", summary["runner_metadata"]["gpu"])

    def test_all_child_artifacts_are_clean_passes_on_same_commit(self) -> None:
        summary = json.loads((ARTIFACT_DIR / "goal2855_summary.json").read_text(encoding="utf-8"))

        for artifact_name in summary["artifacts"]:
            with self.subTest(artifact_name=artifact_name):
                payload = json.loads((ARTIFACT_DIR / artifact_name).read_text(encoding="utf-8"))
                self.assertEqual("pass", payload["status"])
                self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
                self.assertEqual([], payload["source_dirty"])
                self.assertIn("NVIDIA RTX A5000", payload["gpu"])
                boundary = payload.get("claim_boundary", {})
                for key, value in boundary.items():
                    if key.endswith("_claim_authorized") or key == "native_engine_customization":
                        self.assertFalse(value, f"{artifact_name} boundary {key}")

    def test_readiness_packet_uses_goal2893_runner_summary(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "docs/reports/goal2893_current_packet_after_runtime_provenance_index_pod/goal2855_summary.json",
            packet["current_canonical_runner"]["summary_path"],
        )
        self.assertEqual("pass", packet["current_canonical_runner"]["status"])
        self.assertEqual(EXPECTED_COMMIT, packet["current_canonical_runner"]["source_commit"])
        self.assertTrue(packet["required_report_presence"][
            "docs/reports/goal2893_current_packet_after_runtime_provenance_index_2026-05-31.md"
        ])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2893",
            EXPECTED_COMMIT,
            "`all_pass`: true",
            "`claim_boundary_violations`: {}",
            "not a v2.5 release authorization",
            "not a public speedup claim",
            "not true-zero-copy wording",
            "does not prove Tier A/B paper parity",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
