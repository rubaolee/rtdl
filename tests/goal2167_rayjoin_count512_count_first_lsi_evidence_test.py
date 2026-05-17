from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2167_rayjoin_count512_count_first_lsi_evidence_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2167_rayjoin_count_first_optix_lsi_count512_pod_2026-05-16.json"

EXPECTED_COMMIT = "366b5e962a17761091edbcc6a326377ccea714cc"


class Goal2167RayjoinCount512CountFirstLsiEvidenceTest(unittest.TestCase):
    def test_report_records_larger_slice_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("lsi_county256_soil256_count512", text)
        self.assertIn("1.894x", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release authorization", text)

    def test_count512_artifact_records_parity_and_optix_win(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count512"]
        optix = case["backends"]["optix_prepared_lsi"]
        cupy = case["backends"]["cupy_lsi_bruteforce"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertTrue(optix["all_parity_vs_cpu_python_reference"])
        self.assertTrue(cupy["all_parity_vs_cpu_python_reference"])
        self.assertEqual(optix["row_counts"], [269, 269, 269, 269, 269])
        self.assertEqual(optix["row_counts"], cupy["row_counts"])
        self.assertEqual(optix["candidate_pair_count"], 136411275)
        self.assertLess(optix["app_elapsed_sec_median"], cupy["app_elapsed_sec_median"])
        self.assertGreater(
            cupy["app_elapsed_sec_median"] / optix["app_elapsed_sec_median"],
            1.8,
        )


if __name__ == "__main__":
    unittest.main()
