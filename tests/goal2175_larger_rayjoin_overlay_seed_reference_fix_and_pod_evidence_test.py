from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2175_larger_rayjoin_overlay_seed_reference_fix_and_pod_evidence_2026-05-16.md"
)
ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2175_overlay_count256_shared_reference_pod_2026-05-16.json"
)

EXPECTED_COMMIT = "9a4b8ae1ef054406eeda8475a51f24ed3f225459"


class Goal2175LargerRayjoinOverlaySeedEvidenceTest(unittest.TestCase):
    def test_report_records_reference_fix_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("lsi_pairs", text)
        self.assertIn("pip_pairs", text)
        self.assertIn("overlay_county256_soil256", text)
        self.assertIn("1.844x", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("does not authorize", text)

    def test_artifact_records_clean_count256_overlay_evidence(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["overlay_county256_soil256"]
        backends = case["backends"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertEqual(case["workload"], "overlay_seed")
        self.assertEqual(backends["cpu"]["candidate_pair_count"], 56876)
        self.assertEqual(backends["cpu"]["left_polygon_count"], 241)
        self.assertEqual(backends["cpu"]["right_polygon_count"], 236)
        self.assertEqual(case["shared_reference"]["backend"], "cpu_python_reference")
        self.assertEqual(case["shared_reference"]["row_count"], 56876)
        self.assertEqual(
            case["shared_reference"]["reused_by_backends"],
            ["cpu", "embree", "optix", "optix_prepared_overlay_seed"],
        )

        for backend in ("cpu", "embree", "optix", "optix_prepared_overlay_seed"):
            self.assertEqual(backends[backend]["row_counts"], [56876] * 3)
            self.assertTrue(backends[backend]["row_count_consistent"])
            self.assertTrue(backends[backend]["all_parity_vs_cpu_python_reference"])

    def test_artifact_records_optix_same_contract_win_over_embree(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        backends = artifact["cases"]["overlay_county256_soil256"]["backends"]
        embree_sec = backends["embree"]["app_elapsed_sec_median"]
        optix_sec = backends["optix"]["app_elapsed_sec_median"]
        prepared_sec = backends["optix_prepared_overlay_seed"]["app_elapsed_sec_median"]

        self.assertLess(optix_sec, embree_sec)
        self.assertLess(prepared_sec, embree_sec)
        self.assertGreater(embree_sec / optix_sec, 1.8)
        self.assertGreater(embree_sec / prepared_sec, 1.7)
        self.assertLess(optix_sec, prepared_sec)

    def test_artifact_keeps_broad_claims_blocked(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = artifact["claim_boundary"]

        self.assertFalse(boundary["full_rayjoin_reproduction"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_rayjoin_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
