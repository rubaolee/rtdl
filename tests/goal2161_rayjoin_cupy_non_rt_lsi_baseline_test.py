from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2161_rayjoin_cupy_non_rt_lsi_baseline_2026-05-16.md"
COUNT192 = ROOT / "docs" / "reports" / "goal2161_rayjoin_public_cdb_cupy_baseline_count192_pod_2026-05-16.json"
COUNT128_192 = ROOT / "docs" / "reports" / "goal2161_rayjoin_public_cdb_cupy_baseline_count128_192_pod_2026-05-16.json"
RUNNER = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"


class Goal2161RayjoinCupyNonRtLsiBaselineTest(unittest.TestCase):
    def test_report_records_negative_result_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("CuPy CUDA-core all-pairs kernel beats the current RTDL/OptiX median", text)
        self.assertIn("This is a useful loss", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release authorization", text)

    def test_single_case_artifact_records_cupy_as_non_rt_partner_baseline(self) -> None:
        artifact = json.loads(COUNT192.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count192"]
        cupy = case["backends"]["cupy_lsi_bruteforce"]
        optix = case["backends"]["optix"]

        self.assertEqual(artifact["commit"], "28f5c69cf4e84da93c3c01f03c00566a3a516909")
        self.assertFalse(cupy["rt_core_accelerated"])
        self.assertTrue(cupy["partner_accelerated"])
        self.assertEqual(cupy["baseline_kind"], "cupy_rawkernel_cuda_core_bruteforce_lsi")
        self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
        self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
        self.assertEqual(cupy["row_counts"], [85, 85, 85, 85, 85])
        self.assertLess(cupy["app_elapsed_sec_median"], optix["app_elapsed_sec_median"])

    def test_two_case_artifact_preserves_parity_and_cupy_median_lead(self) -> None:
        artifact = json.loads(COUNT128_192.read_text(encoding="utf-8"))

        for case_name in ("lsi_county256_soil256_count128", "lsi_county256_soil256_count192"):
            with self.subTest(case_name=case_name):
                case = artifact["cases"][case_name]
                cupy = case["backends"]["cupy_lsi_bruteforce"]
                optix = case["backends"]["optix"]
                self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
                self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
                self.assertLess(cupy["app_elapsed_sec_median"], optix["app_elapsed_sec_median"])

    def test_runner_source_keeps_cupy_backend_explicitly_non_rt(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("cupy_lsi_bruteforce", text)
        self.assertIn("\"rt_core_accelerated\": False", text)
        self.assertIn("\"partner_accelerated\": True", text)


if __name__ == "__main__":
    unittest.main()
