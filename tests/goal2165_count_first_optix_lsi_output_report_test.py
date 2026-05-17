from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2165_count_first_optix_lsi_output_2026-05-16.md"
COUNT192 = ROOT / "docs" / "reports" / "goal2165_rayjoin_count_first_optix_lsi_count192_pod_2026-05-16.json"
COUNT256 = ROOT / "docs" / "reports" / "goal2165_rayjoin_count_first_optix_lsi_count256_pod_2026-05-16.json"
COUNT384 = ROOT / "docs" / "reports" / "goal2165_rayjoin_count_first_optix_lsi_count384_pod_2026-05-16.json"

EXPECTED_COMMIT = "c204698dd85cdf8f2df263a4f5100429f9798049"


class Goal2165CountFirstOptixLsiOutputReportTest(unittest.TestCase):
    def test_report_records_generic_count_first_protocol_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("count-first candidate output protocol", text)
        self.assertIn("no RayJoin-specific logic was added", text)
        self.assertIn("host exact refinement remains unchanged", text)
        self.assertIn("v2.0 release authorization", text)

    def test_artifacts_are_clean_commit_and_optix_beats_cupy(self) -> None:
        for artifact_path, case_name in (
            (COUNT192, "lsi_county256_soil256_count192"),
            (COUNT256, "lsi_county256_soil256_count256"),
            (COUNT384, "lsi_county256_soil256_count384"),
        ):
            with self.subTest(case_name=case_name):
                artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
                case = artifact["cases"][case_name]
                optix = case["backends"]["optix_prepared_lsi"]
                cupy = case["backends"]["cupy_lsi_bruteforce"]

                self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
                self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
                self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
                self.assertEqual(optix["row_counts"], cupy["row_counts"])
                self.assertEqual(optix["candidate_pair_count"], cupy["candidate_pair_count"])
                self.assertLess(optix["app_elapsed_sec_median"], cupy["app_elapsed_sec_median"])

    def test_larger_slice_speedup_exceeds_one_point_five_x(self) -> None:
        artifact = json.loads(COUNT384.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count384"]
        optix = case["backends"]["optix_prepared_lsi"]["app_elapsed_sec_median"]
        cupy = case["backends"]["cupy_lsi_bruteforce"]["app_elapsed_sec_median"]

        self.assertGreater(cupy / optix, 1.5)


if __name__ == "__main__":
    unittest.main()
