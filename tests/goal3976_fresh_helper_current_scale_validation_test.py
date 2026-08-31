import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3976_fresh_helper_current_scale_validation_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3976_fresh_helper_current_scale_validation_2026-06-08"
SUMMARY = ARTIFACT / "summary.json"


EXPECTED_ROWS = {
    "hausdorff_xhd_scale_default_optix_threshold",
    "spatial_rayjoin_public_cdb_representative_mixed_route_scale_default",
    "rt_dbscan_optix_numba_scale_default_65536_no_validation",
    "robot_collision_optix_scale_default_1024_no_probe_reference",
    "contact_manifold_optix_scale_default_grid64",
    "raydb_style_optix_count_scale_default_262k",
    "barnes_hut_numba_scale_default_8192",
    "librts_spatial_index_optix_scale_default_32768",
    "rtnn_prepared_optix_scale_default_65536",
    "triangle_counting_optix_rt_graph_2a1_scale_default_2048",
}


class Goal3976FreshHelperCurrentScaleValidationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_fresh_helper_run_passed_all_rows(self) -> None:
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        rows = self.summary["rows"]
        self.assertEqual({row["row_id"] for row in rows}, EXPECTED_ROWS)
        self.assertTrue(all(row["status"] == "pass" for row in rows))

    def test_runtime_environment_records_clean_fresh_checkout(self) -> None:
        runtime = self.summary["runtime_environment"]
        self.assertTrue(runtime["working_tree_clean"])
        self.assertEqual(runtime["git_status_short"], [])
        self.assertEqual(
            runtime["source_commit"],
            "62f005d90caca8eeea0d40cbbab430fe890a4fa3",
        )
        self.assertIn("NVIDIA RTX 4000 Ada Generation", runtime["nvidia_smi"])

    def test_helper_smoke_and_toolchain_split_are_recorded(self) -> None:
        helper_stdout = (ARTIFACT / "helper.stdout.log").read_text(encoding="utf-8")
        self.assertIn("partner_smoke_ok", helper_stdout)
        for fragment in [
            "numba==0.60.0",
            "numpy==2.0.2",
            "nvidia-cuda-nvcc-cu12==12.4.131",
            "cupy-cuda12x==14.1.1",
            'export RTDL_CUDA_PREFIX="/usr/local/cuda-12"',
            'export CUDA_HOME="/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc"',
        ]:
            self.assertIn(fragment, helper_stdout)
        build_stdout = (ARTIFACT / "build_optix.stdout.log").read_text(encoding="utf-8")
        self.assertIn("/usr/local/cuda-12/bin/nvcc", build_stdout)

    def test_runner_artifacts_have_no_claim_or_stderr_regression(self) -> None:
        self.assertEqual((ARTIFACT / "run.stderr.log").read_text(encoding="utf-8"), "")
        for flag in [
            "release_authorized",
            "public_speedup_claim_authorized",
            "broad_rt_core_claim_authorized",
            "paper_reproduction_claim_authorized",
        ]:
            self.assertIs(self.summary[flag], False)
        for row in self.summary["rows"]:
            semantic = row.get("semantic_stdout_check", {})
            self.assertTrue(semantic.get("stdout_json_parseable"))
            self.assertEqual(semantic.get("claim_flag_violations"), [])

    def test_report_states_reproducibility_scope_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "fresh-checkout pod runbook step",
            "partner_smoke_ok",
            "all ten current scale-profile rows",
            "does not authorize release",
            "app-specific native-engine logic",
        ]:
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
