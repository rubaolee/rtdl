from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2181_rayjoin_pip_shared_reference_pod_evidence_2026-05-16.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2181_pip512_shared_reference_pod_2026-05-16.json"

EXPECTED_COMMIT = "173a12bca288a9bbddff4386fb1417c4d388be75"


class Goal2181RayjoinPipSharedReferencePodEvidenceTest(unittest.TestCase):
    def test_report_records_pip_boundary_result(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("_run_pip_direct_backend", text)
        self.assertIn("rayjoin_point_location_positive_hits_reference", text)
        self.assertIn("OptiX does not beat Embree", text)
        self.assertIn("does not authorize", text)
        self.assertIn("claims that OptiX wins every RayJoin subproblem", text)

    def test_artifact_records_parity_clean_pip_backends(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = artifact["cases"]["pip_county512"]
        backends = case["backends"]

        self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
        self.assertEqual(case["shared_reference"]["row_count"], 1430)
        self.assertEqual(case["shared_reference"]["reused_by_backends"], ["cpu", "embree", "optix"])
        for backend in ("cpu", "embree", "optix"):
            payload = backends[backend]
            self.assertEqual(payload["row_counts"], [1430] * 5)
            self.assertTrue(payload["row_count_consistent"])
            self.assertTrue(payload["all_parity_vs_cpu_python_reference"])
            self.assertEqual(payload["point_count"], 512)
            self.assertEqual(payload["polygon_count"], 481)
            self.assertEqual(payload["candidate_pair_count"], 246272)

    def test_embree_is_slightly_faster_than_optix_on_this_pip_row(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        backends = artifact["cases"]["pip_county512"]["backends"]
        cpu_sec = backends["cpu"]["app_elapsed_sec_median"]
        embree_sec = backends["embree"]["app_elapsed_sec_median"]
        optix_sec = backends["optix"]["app_elapsed_sec_median"]

        self.assertLess(embree_sec, cpu_sec)
        self.assertLess(optix_sec, cpu_sec)
        self.assertLess(embree_sec, optix_sec)
        self.assertGreater(cpu_sec / embree_sec, 3.5)
        self.assertGreater(cpu_sec / optix_sec, 3.3)
        self.assertLess(embree_sec / optix_sec, 1.0)

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
