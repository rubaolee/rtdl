import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3983_hot_path_scale_up_probe_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3983_hot_path_scale_up_probe_2026-06-08"
SUMMARY = ARTIFACT / "summary.json"


class Goal3983HotPathScaleUpProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.rows = {row["probe"]: row for row in cls.summary["rows"]}

    def test_all_scale_up_probes_completed(self) -> None:
        self.assertEqual(
            set(self.rows),
            {
                "raydb_rows1m",
                "raydb_rows4m",
                "robot_pose8192_obs512",
                "robot_pose16384_obs1024",
            },
        )
        for probe, row in self.rows.items():
            with self.subTest(probe=probe):
                self.assertEqual(row["exit_code"], 0)
                self.assertEqual((ARTIFACT / f"{probe}.exit_code").read_text(encoding="utf-8").strip(), "0")
                self.assertEqual((ARTIFACT / f"{probe}.stderr.txt").read_text(encoding="utf-8"), "")

    def test_raydb_data_scaling_does_not_make_hot_native_call_claim_grade(self) -> None:
        rows1m = self.rows["raydb_rows1m"]
        rows4m = self.rows["raydb_rows4m"]
        self.assertTrue(rows1m["matches_cpu_reference"])
        self.assertTrue(rows4m["matches_cpu_reference"])
        self.assertEqual(rows1m["row_count"], 1_048_576)
        self.assertEqual(rows4m["row_count"], 4_194_304)
        self.assertGreater(rows4m["cold_prepare_total"], 10.0)
        self.assertLess(rows4m["native_call_wall"], 0.01)
        self.assertLess(rows4m["traversal"], 0.01)

    def test_robot_data_scaling_does_not_make_hot_traversal_claim_grade(self) -> None:
        small = self.rows["robot_pose8192_obs512"]
        large = self.rows["robot_pose16384_obs1024"]
        self.assertEqual(small["case_shape"]["segment_count"], 294_912)
        self.assertEqual(large["case_shape"]["segment_count"], 589_824)
        self.assertGreater(large["tail_prepared_query_build_sec"], 3.0)
        self.assertLess(large["tail_traversal_sec"], 0.001)
        self.assertLess(large["tail_total_run_sec"], 0.001)

    def test_report_points_to_batched_hot_query_contract(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "Simple data-size scaling is not enough",
            "resident/batched hot-query contract",
            "keep wrapper/process/setup elapsed separate",
            "not a direct CUDA loader",
            "does not authorize release",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
