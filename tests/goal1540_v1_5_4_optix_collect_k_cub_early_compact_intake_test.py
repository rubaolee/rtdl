from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1540_v1_5_4_optix_collect_k_cub_early_compact_intake_2026-05-08.md"
GOAL1539_JSON = ROOT / "docs" / "reports" / "goal1539_v1_5_4_optix_collect_k_cub_tile_sort_probe_2026-05-08.json"
GOAL1540_JSON = ROOT / "docs" / "reports" / "goal1540_v1_5_4_optix_collect_k_cub_early_compact_probe_2026-05-08.json"


class Goal1540V154OptixCollectKCubEarlyCompactIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(GOAL1540_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "e2fdde4bb1366275fb8e3d33209f40ed121bf16c")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])

    def test_early_compact_improves_over_goal1539(self) -> None:
        goal1539 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1539_JSON.read_text(encoding="utf-8"))["cases"]
        }
        goal1540 = {
            case["candidate_count"]: case
            for case in json.loads(GOAL1540_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                old_stage = goal1539[count]["stage_profile"]["stage_median_ms"]
                new_stage = goal1540[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(new_stage["total_ms"], old_stage["total_ms"])
                self.assertLess(new_stage["merge_sync_ms"], old_stage["merge_sync_ms"] * 0.02)

    def test_intake_records_boundary_and_next_bottleneck(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("strongest measured OptiX `COLLECT_K_BOUNDED`", text)
        self.assertIn("The next bottleneck is again sort", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
