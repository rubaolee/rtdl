import json
import re
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2550_barnes_hut_final_performance_and_closeout_2026-05-23.md"
RTDL_ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal2550_barnes_hut_final_3d_scalar_subtree_pod_32768_2026-05-23.json"
AUTHORS_LOG_DIR = REPO_ROOT / "docs" / "reports" / "goal2550_barnes_hut_authors_new_mode_pod_logs"
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"


class Goal2550BarnesHutFinalPerformanceCloseoutTest(unittest.TestCase):
    def test_final_rtdl_artifact_records_fast_correct_partner_path(self) -> None:
        payload = json.loads(RTDL_ARTIFACT.read_text())
        self.assertEqual(payload["body_count"], 32768)
        self.assertEqual(payload["repeats"], 20)
        self.assertEqual(payload["device"], "NVIDIA RTX A5000")
        self.assertLess(payload["timing_ms"]["resident_kernel_min"], 0.6)
        self.assertEqual(payload["deltas"]["visited_node_total"], 0)
        self.assertEqual(payload["deltas"]["contribution_row_count"], 0)
        self.assertLess(payload["deltas"]["max_scalar_relative_error"], 1.0e-4)
        self.assertFalse(payload["metadata"]["native_engine_app_specific"])
        self.assertFalse(payload["metadata"]["same_tree_contract_as_authors"])
        self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])

    def test_authors_logs_are_orientation_only(self) -> None:
        logs = sorted(AUTHORS_LOG_DIR.glob("*.log"))
        self.assertEqual(len(logs), 5)
        force_times_ms = []
        for path in logs:
            match = re.search(r"RT Cores Force Calculations time: ([0-9.]+)", path.read_text())
            self.assertIsNotNone(match, path.name)
            force_times_ms.append(float(match.group(1)) * 1000.0)
        self.assertLess(min(force_times_ms), 6.0)
        self.assertGreater(min(force_times_ms), 5.0)

    def test_closeout_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "closed for this phase",
            "0.502848 ms",
            "5.405 ms",
            "same-input reload segfaulted",
            "No public speedup ratio is authorized",
            "No native-engine Barnes-Hut or inverse-square force primitive is authorized",
            "partner operator plug-in design",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_readme_records_final_snapshot_without_speedup_claim(self) -> None:
        text = README.read_text()
        self.assertIn("Goal2550 3-D scalar float32 final", text)
        self.assertIn("authors binary segfaulted on direct same-input", text)
        self.assertIn("No speedup ratio should be inferred", text)


if __name__ == "__main__":
    unittest.main()
