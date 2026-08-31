import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3948_current_scale_clean_latest_after_nearest_cubin_hardening_2026-06-08"
)
SUMMARY_JSON = ARTIFACT_DIR / "goal3948_current_scale_clean_52218d79.json"


class Goal3948CurrentScaleCleanLatestAfterNearestCubinHardeningTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    def test_latest_clean_commit_passes_all_current_scale_rows(self) -> None:
        runtime = self.summary["runtime_environment"]
        self.assertEqual("52218d79", runtime["source_commit_short"])
        self.assertTrue(runtime["working_tree_clean"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", runtime["nvidia_smi"])
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(10, self.summary["json_pass_count"])
        self.assertEqual(10, len(self.summary["rows"]))
        self.assertEqual("accept", self.summary["validation"]["status"])

    def test_every_current_scale_row_is_claim_clean(self) -> None:
        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual("pass", row["status"])
                semantic = row["semantic_stdout_check"]
                self.assertTrue(semantic["stdout_json_parseable"])
                self.assertEqual([], semantic["claim_flag_violations"])
                self.assertGreater(row["stdout_bytes"], 0)

    def test_rtnn_remains_clean_after_loader_hardening(self) -> None:
        rows = {row["row_id"]: row for row in self.summary["rows"]}
        rtnn = rows["rtnn_prepared_optix_scale_default_65536"]
        self.assertEqual("pass", rtnn["status"])
        self.assertEqual(0, rtnn["stderr_bytes"])
        stdout = ARTIFACT_DIR / "outputs" / Path(rtnn["stdout_path"]).name
        payload = json.loads(stdout.read_text(encoding="utf-8"))
        self.assertTrue(payload["runner_payload"]["ok"])
        self.assertEqual(
            "fixed_radius_neighbors_3d",
            payload["runner_payload"]["contract"]["family"],
        )

    def test_top_level_claim_boundaries_remain_false(self) -> None:
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(self.summary[flag])


if __name__ == "__main__":
    unittest.main()
