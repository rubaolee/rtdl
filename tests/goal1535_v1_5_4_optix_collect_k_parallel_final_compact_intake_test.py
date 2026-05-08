from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1535_v1_5_4_optix_collect_k_parallel_final_compact_intake_2026-05-08.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1506_v1_5_4_optix_collect_k_stage_profile_probe_2026-05-08.json"
BATCHED_JSON = ROOT / "docs" / "reports" / "goal1530_v1_5_4_optix_collect_k_batched_merge_level_probe_2026-05-08.json"
COMPACT_JSON = ROOT / "docs" / "reports" / "goal1535_v1_5_4_optix_collect_k_parallel_final_compact_probe_2026-05-08.json"


class Goal1535V154OptixCollectKParallelFinalCompactIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(COMPACT_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "78d22ac360df0f14e97f2f06c62a2cd5e86db10f")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])

    def test_long_count_improves_over_baseline_and_batched_level(self) -> None:
        baseline = {case["candidate_count"]: case for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]}
        batched = {case["candidate_count"]: case for case in json.loads(BATCHED_JSON.read_text(encoding="utf-8"))["cases"]}
        compact = {case["candidate_count"]: case for case in json.loads(COMPACT_JSON.read_text(encoding="utf-8"))["cases"]}

        for count in (65537, 131072):
            with self.subTest(candidate_count=count):
                baseline_stage = baseline[count]["stage_profile"]["stage_median_ms"]
                batched_stage = batched[count]["stage_profile"]["stage_median_ms"]
                compact_stage = compact[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(compact_stage["total_ms"], baseline_stage["total_ms"] * 0.40)
                self.assertLess(compact_stage["total_ms"], batched_stage["total_ms"] * 0.90)
                self.assertLess(compact_stage["merge_sync_ms"], batched_stage["merge_sync_ms"] * 0.80)

    def test_topology_records_parallel_final_compact_shape(self) -> None:
        data = json.loads(COMPACT_JSON.read_text(encoding="utf-8"))
        topology_by_count = {
            case["candidate_count"]: case["stage_profile"]["topology"]
            for case in data["cases"]
        }

        self.assertEqual(topology_by_count[4097]["merge_launches"], 3)
        self.assertEqual(topology_by_count[4097]["final_copies"], 0)
        self.assertEqual(topology_by_count[65537]["merge_launches"], 7)
        self.assertEqual(topology_by_count[65537]["metadata_fields_downloaded"], 65)
        self.assertEqual(topology_by_count[131072]["merge_launches"], 7)
        self.assertEqual(topology_by_count[131072]["metadata_fields_downloaded"], 125)

    def test_intake_keeps_experimental_claim_boundary(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("env-gated experimental evidence", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("remaining long-count bottleneck is now level 3", text)
        self.assertIn("apply the same materialize/mark/compact idea", text)


if __name__ == "__main__":
    unittest.main()
