from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1528_v1_5_4_goal1506_pod_stage_profile_intake_2026-05-08.md"
PROFILE_JSON = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
PREFLIGHT_JSON = ROOT / "docs" / "reports" / "goal1508_v1_5_4_optix_collect_k_tiled_preflight_2026-05-08.json"
TRANSCRIPT = ROOT / "docs" / "reports" / "goal1527_v1_5_4_next_pod_stage_profile_transcript_2026-05-08.txt"
PROFILE_JSONL = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.jsonl"


class Goal1528V154Goal1506PodStageProfileIntakeTest(unittest.TestCase):
    def test_profile_json_is_accepted_tiled_path_evidence(self) -> None:
        data = json.loads(PROFILE_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        self.assertEqual(data["git_commit"], "0274ca32d3dd76d7dfc3f4214375db93b8838908")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [4097, 65537, 131072])
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertEqual(case["expected_native_path"], "row_width2_bounded_multi_tile_sort_merge")
                self.assertIs(case["profile_native_path_matches_expected"], True)
                self.assertIs(case["profile_topology_matches_expected"], True)
                self.assertGreater(case["stage_profile"]["stage_median_ms"]["total_ms"], 0.0)

    def test_preflight_accepts_all_target_counts(self) -> None:
        data = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))

        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [4097, 65537, 131072])
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertIs(case["accepted_goal1506_profile_candidate"], True)
                self.assertGreaterEqual(
                    case["max_optin_shared_memory_per_block_bytes"],
                    case["required_shared_memory_bytes"],
                )

    def test_transcript_and_profile_records_are_present(self) -> None:
        transcript = TRANSCRIPT.read_text(encoding="utf-8")
        jsonl_lines = [line for line in PROFILE_JSONL.read_text(encoding="utf-8").splitlines() if line]

        self.assertIn("NVIDIA RTX 2000 Ada Generation", transcript)
        self.assertIn("0274ca32d3dd76d7dfc3f4214375db93b8838908", transcript)
        self.assertIn("Ran 33 tests", transcript)
        self.assertEqual(len(jsonl_lines), 18)

    def test_intake_records_bottleneck_and_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("Accepted Goal1506 pod evidence", text)
        self.assertIn("merge synchronization time", text)
        self.assertIn("Metadata download and final device-to-device copy are small", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
