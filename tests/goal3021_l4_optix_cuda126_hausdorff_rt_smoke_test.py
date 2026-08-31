from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3021_l4_optix_cuda126_hausdorff_rt_smoke_2026-06-02.json"


class Goal3021L4OptixCuda126HausdorffRtSmokeTest(unittest.TestCase):
    def test_report_records_cuda126_unblock_without_speedup_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3021",
            "Goal3020 PTX/toolchain blocker",
            "CUDA 12.6",
            "NVIDIA L4, 565.57.01",
            "aa643d2c272a8106f33b939f688a1cb73f1bd48b",
            "libnvrtc.so.12 => /usr/local/cuda-12.6",
            "rtdl_rt_grouped_reduced_nearest_witness",
            "rt_core_accelerated: true",
            "scalar exact Hausdorff distance parity only",
            "not performance evidence",
            "does not authorize v2.6 release",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_rt_smoke_and_claim_boundaries(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal3021")
        self.assertEqual(data["source_commit"], "aa643d2c272a8106f33b939f688a1cb73f1bd48b")
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["gpu"], "NVIDIA L4, 565.57.01")
        self.assertEqual(data["cuda_prefix"], "/usr/local/cuda-12.6")
        self.assertIn("/usr/local/cuda-12.6", data["linked_nvrtc_line"])
        self.assertTrue(data["rt_core_smoke_passed"])
        self.assertTrue(data["openmp_parity"])

        primary = data["result"]["primary"]
        self.assertEqual(primary["method"], "rtdl_rt_grouped_reduced_nearest_witness")
        self.assertEqual(primary["backend"], "optix")
        self.assertTrue(primary["exact_value"])
        self.assertTrue(primary["rt_core_accelerated"])
        self.assertEqual(primary["threshold_iterations"], 38)

        openmp = data["result"]["comparisons"]["openmp_cpu"]
        self.assertTrue(openmp["matches_primary"])
        self.assertEqual(openmp["distance"], primary["distance"])

        for field in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "package_install_claim_authorized",
        ):
            self.assertFalse(data[field])

    def test_v2_6_roadmap_indexes_goal3021(self) -> None:
        roadmap = rt.v2_6_roadmap()
        self.assertEqual(roadmap["l4_optix_cuda126_smoke_goal"], "Goal3021")
        self.assertIn("cuda12_6", roadmap["l4_optix_cuda126_smoke_status"])
        self.assertIn("not_speedup_evidence", roadmap["l4_optix_cuda126_smoke_status"])
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
