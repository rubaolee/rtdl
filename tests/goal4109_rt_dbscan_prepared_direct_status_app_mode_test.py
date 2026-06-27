from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
REPORT = ROOT / "docs" / "reports" / "goal4109_rt_dbscan_prepared_direct_status_app_mode_2026-06-09.md"
TINY_POD = ROOT / "docs" / "reports" / "goal4109_prepared_direct_status_app_mode_tiny_pod.json"
CLUSTERED_POD = ROOT / "docs" / "reports" / "goal4109_prepared_direct_status_app_mode_clustered65536_pod.json"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4109RtDbscanPreparedDirectStatusAppModeSourceTest(unittest.TestCase):
    def test_app_exposes_prepared_direct_status_mode(self) -> None:
        text = APP.read_text(encoding="utf-8")

        for fragment in (
            "partner_cupy_prepared_direct_status_union_component_signature_3d",
            "prepare_v2_8_fixed_radius_partition_convergence_direct_status_union_cupy_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_direct_status_union_preview_3d",
            "prepared_direct_status_union_app_mode",
            "prepared_direct_status_repeat_protocol",
            "prepared_direct_status_sec",
            "component_signature_sec",
            "graph_component_contract_only",
            "full_dbscan_semantics",
        ):
            self.assertIn(fragment, text)

    def test_prepared_direct_status_mode_rejects_python_rows_before_cupy_is_needed(self) -> None:
        with self.assertRaisesRegex(ValueError, "signature mode does not materialize Python rows"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=True,
                validate=False,
            )

    def test_pod_smoke_artifacts_record_app_mode_boundary(self) -> None:
        tiny = json.loads(TINY_POD.read_text(encoding="utf-8"))
        clustered = json.loads(CLUSTERED_POD.read_text(encoding="utf-8"))

        self.assertEqual(tiny["mode"], "partner_cupy_prepared_direct_status_union_component_signature_3d")
        self.assertEqual(clustered["mode"], "partner_cupy_prepared_direct_status_union_component_signature_3d")
        self.assertTrue(tiny["matches_reference"])
        self.assertIsNone(clustered["matches_reference"])
        self.assertEqual(tiny["signature"]["contract"], "fixed_radius_graph_component_size_signature_3d")
        self.assertEqual(clustered["signature"]["contract"], "fixed_radius_graph_component_size_signature_3d")
        for payload in (tiny, clustered):
            self.assertFalse(payload["claim_boundary"]["full_dbscan"])
            self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
            metadata = payload["metadata"]
            self.assertEqual(metadata["path"], "partner_cupy_prepared_direct_status_union_component_signature_3d")
            self.assertTrue(metadata["prepared_direct_status_union_app_mode"])
            self.assertFalse(metadata["current_default_route"])
            self.assertTrue(metadata["graph_component_contract_only"])
            self.assertFalse(metadata["full_dbscan_semantics"])
            self.assertFalse(metadata["materializes_partition_pair_rows"])
            self.assertFalse(metadata["materializes_near_pair_columns"])
            self.assertTrue(metadata["pair_materialization_avoided"])
            self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
            self.assertFalse(metadata["release_authorized"])
            self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_report_documents_goal4109_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "partner_cupy_prepared_direct_status_union_component_signature_3d",
            "0.531371",
            "0.560136",
            "0.056235",
            "graph-component-signature only",
            "does not promote",
            "does not authorize release",
        ):
            self.assertIn(fragment, report)


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4109RtDbscanPreparedDirectStatusAppModeRuntimeTest(unittest.TestCase):
    def test_prepared_direct_status_app_mode_matches_graph_component_reference(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="partner_cupy_prepared_direct_status_union_component_signature_3d",
            dataset="tiny",
            point_count=None,
            radius=None,
            min_neighbors=None,
            seed=20260519,
            partner="cupy",
            include_rows=False,
            validate=True,
        )

        self.assertTrue(payload["matches_reference"])
        self.assertEqual(payload["signature"]["contract"], "fixed_radius_graph_component_size_signature_3d")
        self.assertEqual(payload["reference_signature"]["contract"], "fixed_radius_graph_component_size_signature_3d")
        self.assertFalse(payload["claim_boundary"]["full_dbscan"])
        self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
        metadata = payload["metadata"]
        self.assertEqual(metadata["path"], "partner_cupy_prepared_direct_status_union_component_signature_3d")
        self.assertTrue(metadata["prepared_direct_status_union_app_mode"])
        self.assertTrue(metadata["prepared_direct_status_union_reused"])
        self.assertTrue(metadata["partition_convergence_hybrid_candidate"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        self.assertFalse(metadata["full_dbscan_semantics"])
        self.assertTrue(metadata["graph_component_contract_only"])
        self.assertFalse(metadata["materializes_python_rows"])
        self.assertFalse(metadata["materializes_full_component_labels"])
        self.assertFalse(metadata["materializes_partition_pair_rows"])
        self.assertFalse(metadata["materializes_near_pair_columns"])
        self.assertTrue(metadata["pair_materialization_avoided"])
        self.assertEqual(metadata["prepared_direct_status_repeat_protocol"]["repeat"], 1)
        self.assertEqual(metadata["prepared_direct_status_repeat_protocol"]["measured_run_count"], 1)
        self.assertTrue(metadata["prepared_direct_status_repeat_protocol"]["signatures_stable"])
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
