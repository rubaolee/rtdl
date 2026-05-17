from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2163_prepared_optix_lsi_build_reuse_2026-05-16.md"
COUNT192 = ROOT / "docs" / "reports" / "goal2163_rayjoin_prepared_optix_lsi_count192_pod_2026-05-16.json"
COUNT256 = ROOT / "docs" / "reports" / "goal2163_rayjoin_prepared_optix_lsi_count256_pod_2026-05-16.json"
COUNT384 = ROOT / "docs" / "reports" / "goal2163_rayjoin_prepared_optix_lsi_count384_pod_2026-05-16.json"
RUNNER = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"

EXPECTED_COMMIT = "3b1e9d86d024497b7772b807ac309e6c41b65219"


class Goal2163PreparedOptixLsiBuildReuseTest(unittest.TestCase):
    def test_report_records_prepared_reuse_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("generic prepared segment-pair-intersection surface", text)
        self.assertIn("not a RayJoin-specific native continuation", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("Prepared vs CuPy", text)

    def test_count192_prepared_removes_one_shot_overhead_and_preserves_parity(self) -> None:
        artifact = json.loads(COUNT192.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count192"]
        optix = case["backends"]["optix"]
        prepared = case["backends"]["optix_prepared_lsi"]
        cupy = case["backends"]["cupy_lsi_bruteforce"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
        self.assertTrue(prepared["all_parity_vs_cpu_python_reference"])
        self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
        self.assertTrue(prepared["rt_core_accelerated"])
        self.assertFalse(prepared["partner_accelerated"])
        self.assertTrue(prepared["prepared_build_side_reused"])
        self.assertLess(prepared["app_elapsed_sec_median"], optix["app_elapsed_sec_median"])
        self.assertLess(abs(prepared["app_elapsed_sec_median"] - cupy["app_elapsed_sec_median"]), 0.0002)

    def test_larger_slices_prepared_optix_beats_cupy_baseline(self) -> None:
        for artifact_path, case_name in (
            (COUNT256, "lsi_county256_soil256_count256"),
            (COUNT384, "lsi_county256_soil256_count384"),
        ):
            with self.subTest(case_name=case_name):
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                case = artifact["cases"][case_name]
                prepared = case["backends"]["optix_prepared_lsi"]
                cupy = case["backends"]["cupy_lsi_bruteforce"]

                self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
                self.assertTrue(prepared["all_parity_vs_cpu_python_reference"])
                self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
                self.assertEqual(prepared["row_counts"], cupy["row_counts"])
                self.assertEqual(prepared["candidate_pair_count"], cupy["candidate_pair_count"])
                self.assertLess(prepared["app_elapsed_sec_median"], cupy["app_elapsed_sec_median"])

    def test_runner_keeps_prepared_backend_explicit_and_generic(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("optix_prepared_lsi", text)
        self.assertIn("prepare_segment_pair_intersection_optix", text)
        self.assertIn("\"prepared_build_side_reused\": True", text)
        self.assertNotIn("rayjoin_prepare", text.lower())


if __name__ == "__main__":
    unittest.main()
