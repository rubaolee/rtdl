from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1543_v1_5_4_optix_collect_k_reuse_workspace_intake_2026-05-08.md"
GOAL1542_JSON = ROOT / "docs" / "reports" / "goal1542_v1_5_4_optix_collect_k_batched_compact_level_probe_2026-05-08.json"
GOAL1543_JSON = ROOT / "docs" / "reports" / "goal1543_v1_5_4_optix_collect_k_reuse_workspace_probe_2026-05-08.json"


class Goal1543V154OptixCollectKReuseWorkspaceIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(GOAL1543_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "ddf7d20e737799e6eab527d61afc412ce5fbab1f")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertEqual(case["stage_profile"]["topology"]["sort_launches"], 1)
                self.assertEqual(case["stage_profile"]["topology"]["merge_launches"], 18 if case["candidate_count"] >= 65537 else 6)

    def test_reuse_workspace_improves_all_counts_over_goal1542(self) -> None:
        goal1542 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1542_JSON.read_text(encoding="utf-8"))["cases"]
        }
        goal1543 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1543_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                old_stage = goal1542[count]["stage_profile"]["stage_median_ms"]
                new_stage = goal1543[count]["stage_profile"]["stage_median_ms"]

                self.assertLess(new_stage["total_ms"], old_stage["total_ms"])
                self.assertLess(new_stage["allocation_ms"], old_stage["allocation_ms"] * 0.01)

    def test_intake_records_workspace_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("workspace reuse, not true zero-copy", text)
        self.assertIn("mutex guards the reusable workspace", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
