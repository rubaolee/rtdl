from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal1956_rawkernel_control_app_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal1956_l4_rawkernel_control_app_partial_no_optix_2026-05-14.md"
SUMMARY = ROOT / "docs" / "reports" / "goal1956_rawkernel_control_app_pod_no_optix" / "summary.json"


class Goal1956RawKernelControlAppPodRunnerTest(unittest.TestCase):
    def test_runner_has_progress_timeouts_and_pod_artifacts(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("STEP_TIMEOUT_SECONDS", text)
        self.assertIn("date -Iseconds", text)
        self.assertIn("progress.log", text)
        self.assertIn("make build-optix", text)
        self.assertIn("RUN_POLYGON_WITH_OPTIX=0", text)
        self.assertIn("skipping OptiX build", text)
        self.assertIn("cupy-cuda12x", text)
        self.assertIn("RTDL_OPTIX_LIBRARY", text)
        self.assertIn("--source-commit-label", text)
        self.assertIn("summary.json", text)

    def test_runner_covers_all_four_rawkernel_control_apps(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        for app in (
            "database_analytics",
            "graph_analytics",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            self.assertIn(app, text)
        self.assertIn("--candidate-backend cpu_all_pairs", text)
        self.assertIn("--candidate-backend \"${polygon_candidate_backend}\"", text)
        self.assertIn("polygon_candidate_backend=\"optix\"", text)

    def test_runner_preserves_claim_boundary(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("\"v2_0_release_authorized\": False", text)
        self.assertIn("\"whole_app_speedup_claim_authorized\": False", text)
        self.assertIn("\"broad_rt_core_speedup_claim_authorized\": False", text)

    def test_partial_l4_report_documents_optix_sdk_blocker(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("partial-no-optix-sdk", text)
        self.assertIn("NVIDIA L4", text)
        self.assertIn("OptiX SDK", text)
        self.assertIn("cpu_all_pairs", text)
        self.assertIn("does not authorize", text)
        self.assertTrue(SUMMARY.exists())


if __name__ == "__main__":
    unittest.main()
