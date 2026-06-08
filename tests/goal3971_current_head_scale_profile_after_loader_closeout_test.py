import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3971_current_head_scale_profile_after_loader_closeout_2026-06-08"
SUMMARY = ARTIFACT_DIR / "summary.json"


class Goal3971CurrentHeadScaleProfileAfterLoaderCloseoutTest(unittest.TestCase):
    def test_pod_summary_is_clean_and_all_ten_rows_pass(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual("e383c4e4", data["runtime_environment"]["source_commit_short"])
        self.assertTrue(data["runtime_environment"]["working_tree_clean"])
        self.assertIn("NVIDIA RTX 4000 Ada Generation", data["runtime_environment"]["nvidia_smi"])
        self.assertTrue(data["all_pass"])
        self.assertEqual(10, data["json_pass_count"])
        self.assertEqual(10, len(data["rows"]))
        self.assertEqual({row["status"] for row in data["rows"]}, {"pass"})

    def test_claim_boundaries_remain_false(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        for key in [
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ]:
            self.assertFalse(data[key], key)
        self.assertIn("does not authorize release action", data["claim_boundary"])

    def test_partner_rows_pass_after_documented_toolchain_setup(self) -> None:
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        rows = {row["app"]: row for row in data["rows"]}
        for app in ["spatial_rayjoin", "rt_dbscan", "barnes_hut"]:
            self.assertEqual("pass", rows[app]["status"], app)

        final_log = (ARTIFACT_DIR / "final_partner_complete_rerun.log").read_text(encoding="utf-8")
        self.assertIn("cupy 14.1.1", final_log)
        self.assertIn('"all_pass": true', final_log)

        cuda124_log = (ARTIFACT_DIR / "numba_cuda124_fix_rerun.log").read_text(encoding="utf-8")
        self.assertIn("numba 0.60.0", cuda124_log)
        self.assertIn("nvidia/cuda_nvcc", cuda124_log)

    def test_runner_progress_log_covers_every_row_and_stderr_is_clean(self) -> None:
        run_stdout = (ARTIFACT_DIR / "run.stdout.log").read_text(encoding="utf-8")
        data = json.loads(SUMMARY.read_text(encoding="utf-8"))
        for row in data["rows"]:
            self.assertIn(f"done {row['row_id']} status=pass", run_stdout)
            self.assertTrue((ARTIFACT_DIR / "outputs" / Path(row["stdout_path"]).name).exists())

        self.assertEqual("", (ARTIFACT_DIR / "run.stderr.log").read_text(encoding="utf-8"))

    def test_report_records_setup_lesson_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "NVIDIA RTX 4000 Ada Generation",
            "numba==0.60.0",
            "nvidia-cuda-nvcc-cu12==12.4.131",
            "cupy-cuda12x==14.1.1",
            "unsupported-PTX-version failures",
            "does not authorize\nrelease",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
