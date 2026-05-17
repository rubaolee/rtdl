from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2169_optix_lsi_device_candidate_filter_2026-05-16.md"
COUNT192 = ROOT / "docs" / "reports" / "goal2169_rayjoin_device_filter_optix_lsi_count192_pod_2026-05-16.json"
COUNT384 = ROOT / "docs" / "reports" / "goal2169_rayjoin_device_filter_optix_lsi_count384_pod_2026-05-16.json"
COUNT512 = ROOT / "docs" / "reports" / "goal2169_rayjoin_device_filter_optix_lsi_count512_pod_2026-05-16.json"

EXPECTED_COMMIT = "3ec61f3971c37c38c7560789c7e87f1233d7358b"


class Goal2169OptixLsiDeviceCandidateFilterReportTest(unittest.TestCase):
    def test_report_records_conservative_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("conservative device-side segment-intersection candidate check", text)
        self.assertIn("host-side `exact_segment_intersection` remains the final correctness authority", text)
        self.assertIn("not a RayJoin-specific native engine path", text)
        self.assertIn("v2.0 release authorization", text)

    def test_artifacts_preserve_parity_and_optix_wins(self) -> None:
        for artifact_path, case_name in (
            (COUNT192, "lsi_county256_soil256_count192"),
            (COUNT384, "lsi_county256_soil256_count384"),
            (COUNT512, "lsi_county256_soil256_count512"),
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
                self.assertLess(optix["app_elapsed_sec_median"], cupy["app_elapsed_sec_median"])

    def test_count512_speedup_stays_above_one_point_eight_x(self) -> None:
        artifact = json.loads(COUNT512.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count512"]
        optix = case["backends"]["optix_prepared_lsi"]["app_elapsed_sec_median"]
        cupy = case["backends"]["cupy_lsi_bruteforce"]["app_elapsed_sec_median"]

        self.assertGreater(cupy / optix, 1.8)


if __name__ == "__main__":
    unittest.main()
