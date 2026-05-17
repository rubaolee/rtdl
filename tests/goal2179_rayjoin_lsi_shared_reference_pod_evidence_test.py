from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2179_rayjoin_lsi_shared_reference_pod_evidence_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2179_lsi512_shared_reference_pod_2026-05-16.json"

EXPECTED_COMMIT = "19a090702c0ea32eee247866743cd44afeb2ede1"


class Goal2179RayjoinLsiSharedReferencePodEvidenceTest(unittest.TestCase):
    def test_report_records_lsi_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("_run_lsi_direct_backend", text)
        self.assertIn("county_zip_join_reference", text)
        self.assertIn("CuPy RawKernel brute force", text)
        self.assertIn("62.472x", text)
        self.assertIn("12.653x", text)
        self.assertIn("does not authorize", text)
        self.assertIn("cold-start OptiX claims", text)

    def test_artifact_records_parity_clean_lsi_backends(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["lsi_county256_soil256_count512"]
        backends = case["backends"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertEqual(case["shared_reference"]["row_count"], 269)
        self.assertEqual(
            case["shared_reference"]["reused_by_backends"],
            ["embree", "optix", "optix_prepared_lsi", "cupy_lsi_bruteforce"],
        )
        for backend in ("embree", "optix", "optix_prepared_lsi", "cupy_lsi_bruteforce"):
            self.assertEqual(backends[backend]["row_counts"], [269, 269, 269])
            self.assertTrue(backends[backend]["row_count_consistent"])
            self.assertTrue(backends[backend]["all_parity_vs_cpu_python_reference"])
            self.assertEqual(backends[backend]["candidate_pair_count"], 136411275)

    def test_optix_beats_embree_and_cupy_bruteforce(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        backends = artifact["cases"]["lsi_county256_soil256_count512"]["backends"]

        optix_sec = backends["optix"]["app_elapsed_sec_median"]
        embree_sec = backends["embree"]["app_elapsed_sec_median"]
        cupy_sec = backends["cupy_lsi_bruteforce"]["app_elapsed_sec_median"]
        prepared_sec = backends["optix_prepared_lsi"]["app_elapsed_sec_median"]

        self.assertLess(optix_sec, embree_sec)
        self.assertLess(optix_sec, cupy_sec)
        self.assertLess(optix_sec, prepared_sec)
        self.assertGreater(embree_sec / optix_sec, 60.0)
        self.assertGreater(cupy_sec / optix_sec, 12.0)
        self.assertGreater(prepared_sec / optix_sec, 6.0)

    def test_claim_boundary_blocks_broad_claims(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = artifact["claim_boundary"]

        self.assertFalse(boundary["full_rayjoin_reproduction"])
        self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_rayjoin_speedup_claim_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
