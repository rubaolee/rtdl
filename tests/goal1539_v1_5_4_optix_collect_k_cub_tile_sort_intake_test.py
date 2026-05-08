from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1539_v1_5_4_optix_collect_k_cub_tile_sort_intake_2026-05-08.md"
BASELINE_JSON = ROOT / "docs" / "reports" / "goal1536_v1_5_4_optix_collect_k_late_level_compact_probe_2026-05-08.json"
CUB_JSON = ROOT / "docs" / "reports" / "goal1539_v1_5_4_optix_collect_k_cub_tile_sort_probe_2026-05-08.json"


class Goal1539V154OptixCollectKCubTileSortIntakeTest(unittest.TestCase):
    def test_probe_is_accepted_clean_pod_evidence(self) -> None:
        data = json.loads(CUB_JSON.read_text(encoding="utf-8"))

        self.assertIs(data["accepted_goal1506_evidence"], True)
        self.assertIs(data["local_fallback_smoke_only"], False)
        self.assertEqual(data["git_commit"], "fe92cebe3c3da35692e079b4bb76a3a008a96c71")
        self.assertEqual(data["device_name"], "NVIDIA RTX 2000 Ada Generation")
        for case in data["cases"]:
            with self.subTest(candidate_count=case["candidate_count"]):
                self.assertTrue(case["same_candidate_rows"])
                self.assertTrue(case["same_valid_count"])
                self.assertTrue(case["same_overflowed_flag"])
                self.assertTrue(case["profile_topology_matches_expected"])

    def test_cub_path_improves_all_target_counts(self) -> None:
        baseline = {
            case["candidate_count"]: case
            for case in json.loads(BASELINE_JSON.read_text(encoding="utf-8"))["cases"]
        }
        cub = {
            case["candidate_count"]: case
            for case in json.loads(CUB_JSON.read_text(encoding="utf-8"))["cases"]
        }

        for count in (4097, 65537, 131072):
            with self.subTest(candidate_count=count):
                baseline_stage = baseline[count]["stage_profile"]["stage_median_ms"]
                cub_stage = cub[count]["stage_profile"]["stage_median_ms"]
                self.assertLess(cub_stage["total_ms"], baseline_stage["total_ms"])
                self.assertLess(cub_stage["sort_sync_ms"], baseline_stage["sort_sync_ms"] * 0.1)

    def test_intake_records_boundary_and_next_bottleneck(self) -> None:
        text = " ".join(REPORT.read_text(encoding="utf-8").split())

        self.assertIn("strongest measured OptiX `COLLECT_K_BOUNDED`", text)
        self.assertIn("current bottleneck is again merge work", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
