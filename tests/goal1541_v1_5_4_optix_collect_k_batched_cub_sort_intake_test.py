from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1541_v1_5_4_optix_collect_k_batched_cub_sort_intake_2026-05-08.md"
GOAL1540_JSON = ROOT / "docs" / "reports" / "goal1540_v1_5_4_optix_collect_k_cub_early_compact_probe_2026-05-08.json"
GOAL1541_JSON = ROOT / "docs" / "reports" / "goal1541_v1_5_4_optix_collect_k_batched_cub_sort_probe_2026-05-08.json"


class Goal1541V154OptixCollectKBatchedCubSortIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(GOAL1541_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "d876074f0681125fbb1631bb080ac2cc838a391a")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])
                self.assertEqual(case["stage_profile"]["topology"]["sort_launches"], 1)

    def test_batched_cub_sort_improves_over_goal1540(self) -> None:
        goal1540 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1540_JSON.read_text(encoding="utf-8"))["cases"]
        }
        goal1541 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1541_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                old_stage = goal1540[count]["stage_profile"]["stage_median_ms"]
                new_stage = goal1541[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(new_stage["total_ms"], old_stage["total_ms"])
                self.assertLess(new_stage["sort_sync_ms"], old_stage["sort_sync_ms"])
                if count >= 65537:
                    self.assertLess(new_stage["sort_sync_ms"], old_stage["sort_sync_ms"] * 0.1)

    def test_intake_records_boundary_and_next_bottleneck(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("strongest measured OptiX `COLLECT_K_BOUNDED`", text)
        self.assertIn("host-side launch orchestration", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
