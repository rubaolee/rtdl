from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.md"
SUMMARY = ROOT / "docs" / "reports" / "goal3062_v2_6_native_tutorial_example_pod_validation_2026-06-02.json"
LOG_DIR = ROOT / "docs" / "reports" / "goal3062_v2_6_native_tutorial_example_pod_validation_logs_2026-06-02"
RELEASE_EXAMPLES = ROOT / "docs" / "release_facing_examples.md"


class Goal3062V26NativeTutorialExamplePodValidationTest(unittest.TestCase):
    def _summary(self) -> dict:
        return json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_summary_records_complete_pod_pass(self) -> None:
        summary = self._summary()

        self.assertTrue(summary["all_pass"])
        self.assertEqual(summary["pass_count"], 21)
        self.assertEqual(summary["total_count"], 21)
        self.assertEqual(len(summary["results"]), 21)

        for result in summary["results"]:
            self.assertEqual(result["status"], "pass", result["name"])
            self.assertEqual(result["returncode"], 0, result["name"])

    def test_pod_identity_and_native_surface_are_recorded(self) -> None:
        summary = self._summary()

        self.assertEqual(summary["commit"], "e126a1b93f138f527ad6d5cff256127dafbf6719")
        self.assertIn("NVIDIA L4", summary["gpu"])
        self.assertIn("580.159.04", summary["gpu"])
        self.assertEqual(summary["cupy"], "14.1.1")
        self.assertEqual(summary["optix_sdk"], "v8.1.0")
        self.assertTrue(summary["rtdl_optix_library"].endswith("build/librtdl_optix.so"))

    def test_required_command_names_are_present(self) -> None:
        names = {result["name"] for result in self._summary()["results"]}

        required = {
            "hello_world",
            "feature_quickstart_cookbook",
            "hausdorff_embree",
            "hausdorff_optix_threshold_rtcore",
            "segment_polygon_anyhit_embree_counts",
            "segment_polygon_anyhit_optix_counts",
            "polygon_pair_overlap_embree_summary",
            "polygon_pair_overlap_optix_summary",
            "partner_anyhit_numpy_embree",
            "partner_anyhit_cupy_cuda_optix",
        }
        self.assertTrue(required.issubset(names))

    def test_log_directory_matches_corrected_run(self) -> None:
        summary = self._summary()

        self.assertTrue(LOG_DIR.exists())
        self.assertEqual(len(list(LOG_DIR.glob("*.log"))), 21)
        for result in summary["results"]:
            self.assertTrue((ROOT / result["log"]).exists(), result["log"])

        stale_failed_log = LOG_DIR / "partner_anyhit_cupy_optix.log"
        self.assertFalse(stale_failed_log.exists())

    def test_public_partner_command_uses_real_parser_choice(self) -> None:
        text = RELEASE_EXAMPLES.read_text(encoding="utf-8")

        self.assertIn("--partner cupy-cuda --backend optix", text)
        self.assertNotIn("--partner cupy --backend optix", text)

    def test_report_keeps_release_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("all_pass=True pass_count=21 total=21", text)
        self.assertIn("does not authorize the v2.6 release button", text)
        self.assertIn("final release consensus record", text)
        self.assertIn("general zero-copy/device-residency claims", text)
        self.assertNotIn("release authorized", text.lower())


if __name__ == "__main__":
    unittest.main()
