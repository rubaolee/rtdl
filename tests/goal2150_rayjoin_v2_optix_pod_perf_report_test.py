from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2150_rayjoin_v2_optix_pod_perf_and_shape_pair_fix_2026-05-16.md"
ENV = ROOT / "docs" / "reports" / "goal2150_rayjoin_v2_pod_environment_2026-05-16.txt"
MEDIUM = ROOT / "docs" / "reports" / "goal2150_rayjoin_v2_scale_perf_medium_pod_2026-05-16.json"
LARGE = ROOT / "docs" / "reports" / "goal2150_rayjoin_v2_scale_perf_large_pip_lsi_pod_2026-05-16.json"


class Goal2150RayjoinV2OptixPodPerfReportTest(unittest.TestCase):
    def test_report_records_fix_results_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "segment_pair_intersection_hit",
            "This is not RayJoin app customization",
            "NVIDIA RTX 4000 Ada Generation",
            "OptiX wins PIP and LSI",
            "Large disjoint PIP does not favor OptiX",
            "full RayJoin paper reproduction",
            "broad RT-core speedup claims",
            "not a release gate closure",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_artifacts_preserve_parity_and_claim_flags(self) -> None:
        for artifact in (MEDIUM, LARGE):
            with self.subTest(artifact=artifact.name):
                payload = json.loads(artifact.read_text(encoding="utf-8"))
                self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])
                for workload in payload["workloads"].values():
                    for backend in workload["backends"].values():
                        self.assertTrue(backend["parity_vs_cpu_python_reference"])

    def test_environment_records_commit_and_toolchain(self) -> None:
        text = ENV.read_text(encoding="utf-8")

        self.assertIn("b05c07df0c1e08d7babf3b17fdee85febffb711f", text)
        self.assertIn("NVIDIA RTX 4000 Ada Generation", text)
        self.assertIn("RTDL_OPTIX_PTX_COMPILER=nvcc", text)
        self.assertIn("RTDL_EMBREE_PREFIX=/usr", text)


if __name__ == "__main__":
    unittest.main()
