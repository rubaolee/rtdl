from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2157_rayjoin_public_cdb_nonzero_lsi_slice_evidence_2026-05-16.md"
SMALL = ROOT / "docs" / "reports" / "goal2157_rayjoin_public_cdb_nonzero_lsi_slice_pod_2026-05-16.json"
LARGE = ROOT / "docs" / "reports" / "goal2157_rayjoin_public_cdb_nonzero_lsi_larger_slices_pod_2026-05-16.json"


class Goal2157RayjoinPublicCdbNonzeroLsiSliceEvidenceTest(unittest.TestCase):
    def test_report_records_nonzero_lsi_results_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "real cross-dataset line-segment intersections",
            "county start: `256`",
            "soil start: `256`",
            "`count192`",
            "5.18x",
            "bounded derived-input evidence",
            "full RayJoin paper reproduction",
            "v2.0 release authorization",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_artifacts_show_nonzero_rows_and_parity(self) -> None:
        small = json.loads(SMALL.read_text(encoding="utf-8"))
        large = json.loads(LARGE.read_text(encoding="utf-8"))

        self.assertEqual(small["commit"], "9931585362e0e27ccf1a4e657afc7fd670209041")
        self.assertEqual(large["commit"], "9931585362e0e27ccf1a4e657afc7fd670209041")
        self.assertFalse(small["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(large["claim_boundary"]["v2_0_release_authorized"])

        self.assertEqual(small["case"]["backends"]["optix"]["row_counts"], [34, 34, 34, 34, 34])
        self.assertTrue(small["case"]["backends"]["optix"]["all_parity_vs_cpu_python_reference"])

        count192 = large["cases"]["lsi_county_start256_soil_start256_count192"]
        self.assertEqual(count192["backends"]["optix"]["row_counts"], [85, 85, 85, 85, 85])
        for backend, row in count192["backends"].items():
            with self.subTest(backend=backend):
                self.assertEqual(row["status"], "ok")
                self.assertTrue(row["all_parity_vs_cpu_python_reference"])

        optix = count192["backends"]["optix"]["app_elapsed_sec_median"]
        cpu = count192["backends"]["cpu"]["app_elapsed_sec_median"]
        embree = count192["backends"]["embree"]["app_elapsed_sec_median"]
        self.assertLess(optix, cpu)
        self.assertLess(optix, embree)


if __name__ == "__main__":
    unittest.main()
