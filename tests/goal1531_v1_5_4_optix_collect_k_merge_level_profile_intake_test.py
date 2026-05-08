from pathlib import Path
import json
import statistics
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1531_v1_5_4_optix_collect_k_merge_level_profile_intake_2026-05-08.md"
PROBE_JSON = ROOT / "docs" / "reports" / "goal1531_v1_5_4_optix_collect_k_merge_level_profile_probe_2026-05-08.json"
PROFILE_JSONL = ROOT / "docs" / "reports" / "goal1531_v1_5_4_optix_collect_k_merge_level_profile_probe_2026-05-08.jsonl"


class Goal1531V154OptixCollectKMergeLevelProfileIntakeTest(unittest.TestCase):
    def test_probe_is_clean_pod_accepted_evidence(self) -> None:
        data = json.loads(PROBE_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertEqual(data["git_commit"], "fc24b7646d7526346b878b0394f3dd0802221d43")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        self.assertEqual([case["candidate_count"] for case in data["cases"]], [4097, 65537, 131072])
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertTrue(case["profile_native_path_matches_expected"])

    def test_jsonl_records_per_level_profile(self) -> None:
        records = [
            json.loads(line)
            for line in PROFILE_JSONL.read_text(encoding="utf-8").splitlines()
            if line
        ]

        last_131k = [record for record in records if record["candidate_count"] == 131072][-5:]
        self.assertEqual(len(last_131k), 5)
        for record in last_131k:
            with self.subTest(total_ms=record["total_ms"]):
                levels = record["merge_level_profile"]
                self.assertEqual([level["pair_count"] for level in levels], [16, 8, 4, 2, 1])
                self.assertEqual([level["output_capacity"] for level in levels], [8192, 16384, 32768, 65536, 131072])
                self.assertGreater(levels[-1]["sync_ms"], 10.0)

    def test_late_large_levels_dominate_131k_merge_sync(self) -> None:
        records = [
            json.loads(line)
            for line in PROFILE_JSONL.read_text(encoding="utf-8").splitlines()
            if line and json.loads(line)["candidate_count"] == 131072
        ][-5:]

        level3 = statistics.median(record["merge_level_profile"][3]["sync_ms"] for record in records)
        level4 = statistics.median(record["merge_level_profile"][4]["sync_ms"] for record in records)
        total_merge = statistics.median(record["merge_sync_ms"] for record in records)

        self.assertGreater(level3 + level4, total_merge * 0.65)
        self.assertGreater(level4, 10.0)
        self.assertLess(total_merge, 30.0)

    def test_intake_records_next_parallel_merge_target(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("levels 3 and 4 account for roughly", text)
        self.assertIn("true parallel merge/compact kernel", text)
        self.assertIn("Preserves fail-closed overflow behavior", text)


if __name__ == "__main__":
    unittest.main()
