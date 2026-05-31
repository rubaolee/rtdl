from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import rtdsl as rt
from scripts import goal2797_triangle_counting_v25_canonical_harness as harness


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2797_triangle_counting_v2_5_canonical_harness_2026-05-31.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2797_triangle_counting_v2_5_canonical_harness_consensus_2026-05-31.md"
)
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2797_pod_artifacts"
    / "triangle_counting_v25_canonical_harness_5000_optix.json"
)


class Goal2797TriangleCountingV25CanonicalHarnessTest(unittest.TestCase):
    def test_disjoint_triangle_generator_has_expected_oracle_shape(self) -> None:
        edges = harness.disjoint_triangle_edges(2)

        self.assertEqual(edges, ((0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5)))

    def test_cpu_harness_matches_oracle_for_both_lowerings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = harness.run_goal2797_triangle_counting_harness(
                triangle_counts=(2,),
                backends=("cpu",),
                warmup=0,
                repeat=1,
                use_cupy_for_2a1_optix=False,
                work_dir=Path(tmp),
                fail_fast=True,
            )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["row_count"], 2)
        for row in payload["rows"]:
            with self.subTest(method=row["method"]):
                self.assertEqual(row["oracle_triangle_count"], 2)
                self.assertEqual(row["result_triangle_count"], 2)
                self.assertTrue(row["triangle_count_matches_oracle"])
                self.assertIn("same_contract_native_timing", row)
                self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])

    def test_manifest_records_goal2797_canonical_harness_status(self) -> None:
        manifest = rt.v2_5_tiered_benchmark_manifest()
        row = next(app for app in manifest["apps"] if app["app_id"] == "triangle_counting")

        self.assertEqual(row["canonical_harness_status"], "ready_with_goal2797_canonical_harness")
        self.assertIn("Goal2797", row["pod_evidence_status"])
        self.assertIn("canonical harness", row["next_action"])
        self.assertEqual(rt.validate_v2_5_tiered_benchmark_manifest()["status"], "accept")

    def test_pod_artifact_records_optix_same_contract_rows(self) -> None:
        artifact = POD_ARTIFACT.read_text(encoding="utf-8")
        self.assertIn('"status": "pass"', artifact)
        self.assertIn('"rt_graph_2a1_generic_rt"', artifact)
        self.assertIn('"rt_graph_1a2_generic_rt"', artifact)
        self.assertIn('"rt_core_accelerated": true', artifact)
        self.assertIn('"public_speedup_claim_authorized": false', artifact)

    def test_report_and_consensus_record_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Triangle Counting v2.5 Canonical Harness", report)
        self.assertIn("Goal2797", consensus)
        self.assertIn("accept-with-boundary", consensus)
        self.assertIn("not a public speedup claim", report)


if __name__ == "__main__":
    unittest.main()
