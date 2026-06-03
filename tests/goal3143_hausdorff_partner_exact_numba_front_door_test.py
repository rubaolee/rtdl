from __future__ import annotations

import math
import unittest
import json
from pathlib import Path

import rtdsl as rt
from examples.v2_0.research_benchmarks.hausdorff_xhd import rtdl_hausdorff_distance_app as hausdorff
from rtdsl.reference import Point


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_SOURCE = REPO_ROOT / "src" / "rtdsl" / "partner_adapters.py"
NUMBA_SOURCE = REPO_ROOT / "src" / "rtdsl" / "numba_partner_continuation.py"
APP_SOURCE = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "hausdorff_xhd" / "rtdl_hausdorff_distance_app.py"
REPORT = REPO_ROOT / "docs" / "reports" / "goal3143_hausdorff_partner_exact_numba_front_door_2026-06-03.md"
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal3143_pod_artifacts"
    / "hausdorff_partner_exact_numba_pod_probe_2026-06-03.json"
)


class Goal3143HausdorffPartnerExactNumbaFrontDoorTest(unittest.TestCase):
    def test_sources_expose_shared_numba_hausdorff_front_door(self) -> None:
        adapter = ADAPTER_SOURCE.read_text(encoding="utf-8")
        numba = NUMBA_SOURCE.read_text(encoding="utf-8")
        app = APP_SOURCE.read_text(encoding="utf-8")

        for phrase in (
            "NUMBA_SQRT_F64_OPERATION",
            "describe_numba_sqrt_f64",
            "run_numba_sqrt_f64",
            "_numba_sqrt_f64_kernel",
        ):
            self.assertIn(phrase, numba)
        for phrase in (
            'if partner == "numba"',
            "_directed_hausdorff_2d_numba_partner_columns",
            "pairwise_l2_sq_block_nearest_rows_2d_partner_columns",
            "group_argmin_then_global_argmax_partner_columns",
            "v2_8_partner_continuation_operations",
            "materialize_nearest_distances",
            "sqrt_f64",
        ):
            self.assertIn(phrase, adapter)
        self.assertIn('choices=("torch", "cupy", "numba")', app)

    def test_sqrt_descriptor_is_generic(self) -> None:
        descriptor = rt.describe_numba_sqrt_f64()
        self.assertEqual(descriptor["operation"], "sqrt_f64")
        self.assertEqual(descriptor["partner"], "numba")
        self.assertTrue(descriptor["elementwise_transform"])
        self.assertFalse(descriptor["host_column_materialization_used"])
        self.assertFalse(descriptor["replaces_rt_traversal"])

    def test_report_and_artifact_keep_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "partner_exact",
            "partner=\"numba\"",
            "materialize_nearest_distances=False",
            "not an RT-core path",
            "does not authorize public speedup",
            "NVIDIA RTX 4000 Ada Generation",
        ):
            self.assertIn(phrase, report)

        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(artifact["goal"], "Goal3143")
        self.assertTrue(artifact["all_match"])
        self.assertEqual(artifact["gpu"], "NVIDIA RTX 4000 Ada Generation")
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)
        modes = {row["mode"] for row in artifact["rows"]}
        self.assertEqual(modes, {"partner_exact_numba", "partner_numba_block_nearest_exact"})
        for row in artifact["rows"]:
            self.assertTrue(row["matches_oracle"])
            self.assertFalse(row["host_score_row_materialization_used"])
            self.assertTrue(row["score_rows_generated_on_partner_device"])
            self.assertFalse(row["rt_core_accelerated"])

    def test_directed_adapter_executes_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable shared-front-door validation")

        source = (
            Point(id=10, x=0.0, y=0.0),
            Point(id=11, x=2.0, y=0.0),
        )
        target = (
            Point(id=20, x=0.0, y=1.0),
            Point(id=21, x=3.0, y=0.0),
        )
        source_columns = rt.point_rows_to_partner_columns(source, partner="numba")
        target_columns = rt.point_rows_to_partner_columns(target, partner="numba")
        self.assertEqual(source_columns["ids"].copy_to_host().dtype.name, "int64")

        payload = rt.directed_hausdorff_2d_partner_columns(
            source_columns,
            target_columns,
            partner="numba",
            return_metadata=True,
        )
        metadata = payload["metadata"]
        columns = payload["columns"]
        self.assertEqual(metadata["partner"], "numba")
        self.assertEqual(metadata["numba_strategy"], "block_nearest_rows")
        self.assertEqual(metadata["numba_score_row_operation"], "pairwise_l2_sq_block_nearest_rows_2d")
        self.assertEqual(metadata["source_id"], 10)
        self.assertEqual(metadata["target_id"], 20)
        self.assertTrue(math.isclose(metadata["distance"], 1.0, rel_tol=0.0, abs_tol=1e-12))
        self.assertFalse(metadata["host_score_row_materialization_used"])
        self.assertTrue(metadata["nearest_distance_column_materialized"])
        self.assertTrue(metadata["score_rows_generated_on_partner_device"])
        self.assertEqual(metadata["v2_8_partner_continuation_operations_semantics"], "executed_operations_this_call")
        self.assertIn("sqrt_f64", metadata["v2_8_partner_continuation_operations"])
        self.assertEqual(columns["nearest_target_ids"].copy_to_host().tolist(), [20, 21])
        self.assertEqual(columns["nearest_distances"].copy_to_host().tolist(), [1.0, 1.0])

    def test_hausdorff_app_partner_exact_accepts_numba_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is required for executable app validation")

        payload = hausdorff.run_app("partner_exact", copies=2, partner="numba")
        self.assertEqual(payload["backend"], "partner_exact")
        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["numba_strategy"], "block_nearest_rows")
        self.assertFalse(payload["host_score_row_materialization_used"])
        self.assertFalse(payload["directed_a_to_b"]["nearest_distance_column_materialized"])
        self.assertEqual(
            payload["directed_a_to_b"]["v2_8_partner_continuation_operations_semantics"],
            "executed_operations_this_call",
        )
        self.assertNotIn("sqrt_f64", payload["directed_a_to_b"]["v2_8_partner_continuation_operations"])
        self.assertTrue(payload["score_rows_generated_on_partner_device"])
        self.assertFalse(payload["claim_boundary"]["numba_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
