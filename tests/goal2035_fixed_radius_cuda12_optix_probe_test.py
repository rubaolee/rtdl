from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2035_fixed_radius_cuda12_optix_probe_2026-05-14.md"
JSON_REPORT = ROOT / "docs" / "reports" / "goal2035_fixed_radius_cuda12_optix_probe_2026-05-14.json"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2035_fixed_radius_cuda12_probe"


class Goal2035FixedRadiusCuda12OptixProbeTest(unittest.TestCase):
    def test_report_documents_the_actual_repair_recipe(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("make build-optix CUDA_PREFIX=/usr/local/cuda-12", text)
        self.assertIn("RTDL_OPTIX_PTX_COMPILER=nvcc", text)
        self.assertIn("RTDL_NVCC=/usr/local/cuda-12/bin/nvcc", text)
        self.assertIn("RTDL_NVCC_CCBIN=/usr/bin/g++", text)
        self.assertIn("not v2.0 release authorization", text)

    def test_json_pins_probe_result_and_blocks_release_claims(self) -> None:
        payload = json.loads(JSON_REPORT.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "development-evidence-not-release-authorization")
        self.assertEqual(payload["toolchain_repair"]["linked_nvrtc"], "libnvrtc.so.12")
        self.assertEqual(payload["toolchain_repair"]["ptx_compiler"], "nvcc")
        self.assertLess(payload["small_probe"]["v2_vs_v1_8_prepared_ratio"], 0.6)
        self.assertTrue(payload["small_probe"]["parity"]["counts_match"])
        self.assertTrue(payload["small_probe"]["parity"]["summary_match"])
        self.assertEqual(payload["large_probe"]["status"], "pass")
        self.assertTrue(payload["large_probe"]["all_rows_passed_parity"])
        self.assertLess(payload["large_probe"]["ratios"]["facility_knn_assignment"], 0.02)
        self.assertLess(payload["large_probe"]["ratios"]["hausdorff_distance_reverse"], 0.005)
        self.assertLess(payload["large_probe"]["ratios"]["ann_candidate_search"], 0.03)
        self.assertFalse(payload["claim_boundary"]["v2_0_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_rt_core_speedup_claim_authorized"])

    def test_pod_artifacts_are_present_and_show_success(self) -> None:
        probe = json.loads((ARTIFACT_DIR / "fixed_radius_cuda12_nvcc_gpp_probe.json").read_text(encoding="utf-8"))
        large = json.loads((ARTIFACT_DIR / "fixed_radius_cuda12_large_probe.json").read_text(encoding="utf-8"))
        build_log = (ARTIFACT_DIR / "build_optix_cuda12_override.log").read_text(encoding="utf-8")
        probe_log = (ARTIFACT_DIR / "fixed_radius_cuda12_nvcc_gpp_probe.log").read_text(encoding="utf-8")
        large_log = (ARTIFACT_DIR / "fixed_radius_cuda12_large_probe.log").read_text(encoding="utf-8")

        self.assertEqual(probe["status"], "pass")
        self.assertEqual(large["status"], "pass")
        self.assertEqual(len(large["results"]), 6)
        self.assertIn("/usr/local/cuda-12/bin/nvcc", build_log)
        self.assertIn('"status": "pass"', probe_log)
        self.assertIn("status=0", large_log)
        self.assertIn("v2_vs_v1_8_prepared_ratio", probe_log)


if __name__ == "__main__":
    unittest.main()
