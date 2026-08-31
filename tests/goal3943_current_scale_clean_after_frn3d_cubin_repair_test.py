import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal3943_current_scale_clean_after_frn3d_cubin_repair_2026-06-08"
)
SUMMARY_JSON = ARTIFACT_DIR / "goal3943_current_scale_clean_d792b037.json"


class Goal3943CurrentScaleCleanAfterFrn3dCubinRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))

    def test_clean_commit_and_full_row_pass(self) -> None:
        runtime = self.summary["runtime_environment"]
        self.assertEqual("d792b037", runtime["source_commit_short"])
        self.assertTrue(runtime["working_tree_clean"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", runtime["nvidia_smi"])
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(10, self.summary["json_pass_count"])
        self.assertEqual(10, len(self.summary["rows"]))
        self.assertEqual("accept", self.summary["validation"]["status"])

    def test_every_row_is_parseable_and_claim_clean(self) -> None:
        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual("pass", row["status"])
                semantic = row["semantic_stdout_check"]
                self.assertTrue(semantic["stdout_json_parseable"])
                self.assertEqual([], semantic["claim_flag_violations"])
                self.assertGreater(row["stdout_bytes"], 0)

    def test_rtnn_row_closes_ptx_toolchain_failure(self) -> None:
        rows = {row["row_id"]: row for row in self.summary["rows"]}
        rtnn = rows["rtnn_prepared_optix_scale_default_65536"]
        self.assertEqual("pass", rtnn["status"])
        self.assertEqual(0, rtnn["stderr_bytes"])
        stdout = ARTIFACT_DIR / "outputs" / Path(rtnn["stdout_path"]).name
        payload = json.loads(stdout.read_text(encoding="utf-8"))
        runner = payload["runner_payload"]
        self.assertTrue(runner["ok"])
        self.assertEqual("", runner["error"])
        self.assertEqual("fixed_radius_neighbors_3d", runner["contract"]["family"])

    def test_boundary_flags_remain_false(self) -> None:
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ):
            self.assertFalse(self.summary[flag])


if __name__ == "__main__":
    unittest.main()
