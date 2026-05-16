from __future__ import annotations

import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts import goal2147_rayjoin_v2_scale_perf as perf

REPORT = ROOT / "docs" / "reports" / "goal2147_rayjoin_v2_scale_perf_harness_2026-05-16.md"
QUICK_ARTIFACT = ROOT / "docs" / "reports" / "goal2147_rayjoin_v2_scale_perf_quick_local_2026-05-16.json"
LINUX_QUICK_ARTIFACT = ROOT / "docs" / "reports" / "goal2147_rayjoin_v2_scale_perf_quick_linux_2026-05-16.json"
LINUX_MEDIUM_ARTIFACT = ROOT / "docs" / "reports" / "goal2147_rayjoin_v2_scale_perf_medium_pip_lsi_linux_2026-05-16.json"


class Goal2147RayjoinV2ScalePerfTest(unittest.TestCase):
    def test_quick_scale_shapes_have_meaningful_positive_rows(self) -> None:
        pip_case = perf.make_case("pip", "quick")
        lsi_case = perf.make_case("lsi", "quick")
        overlay_case = perf.make_case("overlay_seed", "quick")

        self.assertEqual(len(pip_case["points"]), 64)
        self.assertEqual(len(pip_case["polygons"]), 32)
        self.assertEqual(len(lsi_case["left"]), 32)
        self.assertEqual(len(lsi_case["right"]), 32)
        self.assertEqual(len(overlay_case["left"]), 32)
        self.assertEqual(len(overlay_case["right"]), 32)

    def test_quick_cpu_suite_preserves_boundaries_and_contracts(self) -> None:
        payload = perf.run_suite(
            scale="quick",
            workloads=("pip", "lsi", "overlay_seed"),
            backends=("cpu",),
            repeats=1,
            warmups=0,
        )

        self.assertFalse(payload["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(payload["claim_boundary"]["paper_scale_perf_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertEqual(
            payload["workloads"]["pip"]["output_contract"],
            "point_to_polygon_positive_hit_rows",
        )
        self.assertEqual(
            payload["workloads"]["lsi"]["reference_row_count"],
            1024,
        )
        self.assertEqual(
            payload["workloads"]["overlay_seed"]["output_contract"],
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
        )
        self.assertEqual(
            payload["workloads"]["overlay_seed"]["reference_summary"]["active_seed_count"],
            32,
        )

    def test_report_and_quick_artifact_record_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = QUICK_ARTIFACT.read_text(encoding="utf-8")

        for phrase in (
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
            "progress logging",
            "full RayJoin paper reproduction",
            "RT-core speedup claims",
            "Serious RT-core evidence starts at the next pod run",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report)
        self.assertIn('"rt_core_speedup_claim_authorized": false', artifact)
        self.assertIn('"parity_vs_cpu_python_reference": true', artifact)
        self.assertIn("goal2147_rayjoin_v2_scale_perf_quick_linux_2026-05-16.json", report)
        self.assertIn("future pod tables must use warmups", report)

    def test_linux_artifacts_keep_claims_bounded(self) -> None:
        for artifact_path in (LINUX_QUICK_ARTIFACT, LINUX_MEDIUM_ARTIFACT):
            with self.subTest(artifact=artifact_path.name):
                artifact = artifact_path.read_text(encoding="utf-8")
                self.assertIn('"rt_core_speedup_claim_authorized": false', artifact)
                self.assertIn('"parity_vs_cpu_python_reference": true', artifact)


if __name__ == "__main__":
    unittest.main()
