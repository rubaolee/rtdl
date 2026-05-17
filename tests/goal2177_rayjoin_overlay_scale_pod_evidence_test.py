from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2177_rayjoin_overlay_scale_pod_evidence_2026-05-16.md"
ARTIFACT_384 = ROOT / "docs" / "reports" / "goal2177_overlay384_scale_pod_2026-05-16.json"
ARTIFACT_512 = ROOT / "docs" / "reports" / "goal2177_overlay512_scale_pod_2026-05-16.json"

EXPECTED_COMMIT = "f161c8aafdfc0a469c4e23f92859b810e9f9b8be"


class Goal2177RayjoinOverlayScalePodEvidenceTest(unittest.TestCase):
    def test_report_records_scale_trend_and_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("overlay_county384_soil384", text)
        self.assertIn("overlay_county512_soil512", text)
        self.assertIn("2.619x", text)
        self.assertIn("3.688x", text)
        self.assertIn("does not authorize", text)
        self.assertIn("v2.0 release authorization", text)
        self.assertIn("stronger CUDA/CuPy spatial-prefilter baselines", text)

    def test_artifacts_are_parity_clean(self) -> None:
        for path, case_name, rows in (
            (ARTIFACT_384, "overlay_county384_soil384", 130320),
            (ARTIFACT_512, "overlay_county512_soil512", 233766),
        ):
            with self.subTest(case=case_name):
                artifact = json.loads(path.read_text(encoding="utf-8"))
                case = artifact["cases"][case_name]
                self.assertEqual(artifact["commit"], EXPECTED_COMMIT)
                self.assertEqual(case["shared_reference"]["row_count"], rows)
                self.assertEqual(
                    case["shared_reference"]["reused_by_backends"],
                    ["cpu", "embree", "optix", "optix_prepared_overlay_seed"],
                )
                for backend in ("cpu", "embree", "optix", "optix_prepared_overlay_seed"):
                    payload = case["backends"][backend]
                    self.assertEqual(payload["row_counts"], [rows, rows, rows])
                    self.assertTrue(payload["row_count_consistent"])
                    self.assertTrue(payload["all_parity_vs_cpu_python_reference"])

    def test_optix_advantage_widens_with_scale(self) -> None:
        artifact_384 = json.loads(ARTIFACT_384.read_text(encoding="utf-8"))
        artifact_512 = json.loads(ARTIFACT_512.read_text(encoding="utf-8"))
        backends_384 = artifact_384["cases"]["overlay_county384_soil384"]["backends"]
        backends_512 = artifact_512["cases"]["overlay_county512_soil512"]["backends"]

        ratio_384 = backends_384["embree"]["app_elapsed_sec_median"] / backends_384["optix"]["app_elapsed_sec_median"]
        ratio_512 = backends_512["embree"]["app_elapsed_sec_median"] / backends_512["optix"]["app_elapsed_sec_median"]

        self.assertGreater(ratio_384, 2.5)
        self.assertGreater(ratio_512, 3.6)
        self.assertGreater(ratio_512, ratio_384)
        self.assertLess(
            backends_512["optix"]["app_elapsed_sec_median"],
            backends_512["optix_prepared_overlay_seed"]["app_elapsed_sec_median"],
        )

    def test_claim_boundary_blocks_release_and_whole_app_claims(self) -> None:
        for path in (ARTIFACT_384, ARTIFACT_512):
            artifact = json.loads(path.read_text(encoding="utf-8"))
            boundary = artifact["claim_boundary"]

            self.assertFalse(boundary["full_rayjoin_reproduction"])
            self.assertFalse(boundary["paper_scale_perf_claim_authorized"])
            self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
            self.assertFalse(boundary["whole_app_rayjoin_speedup_claim_authorized"])
            self.assertFalse(boundary["v2_0_release_authorized"])


if __name__ == "__main__":
    unittest.main()
