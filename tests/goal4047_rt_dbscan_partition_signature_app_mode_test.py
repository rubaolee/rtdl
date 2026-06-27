from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from examples.benchmark_apps.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    _component_size_signature_payload,
    run_rt_dbscan_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal4047_rt_dbscan_partition_signature_app_mode_2026-06-08.md"
POD_SMOKE = ROOT / "docs" / "reports" / "goal4047_rt_dbscan_partition_signature_app_mode_pod_smoke.json"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4047RtDbscanPartitionSignatureSourceTest(unittest.TestCase):
    def test_app_and_docs_expose_explicit_candidate_mode(self) -> None:
        text = APP.read_text(encoding="utf-8") + "\n" + README.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")

        for fragment in (
            "partner_cupy_partition_convergence_component_signature_3d",
            "build_v2_8_fixed_radius_partition_convergence_component_signature_cupy_preview_3d",
            "fixed_radius_graph_component_size_signature_3d",
            "partition_convergence_hybrid_candidate",
            "partition_convergence_hybrid_promoted",
            "graph_component_contract_only",
            "full_dbscan_semantics",
        ):
            self.assertIn(fragment, text)

    def test_component_size_signature_payload_is_generic(self) -> None:
        payload = _component_size_signature_payload([4, 1, 4, 0, 2])

        self.assertEqual(payload["component_sizes"], (1, 2, 4, 4))
        self.assertEqual(payload["component_count"], 4)
        self.assertEqual(payload["point_count"], 11)
        self.assertEqual(payload["contract"], "fixed_radius_graph_component_size_signature_3d")

    def test_signature_mode_rejects_python_rows_before_cupy_is_needed(self) -> None:
        with self.assertRaisesRegex(ValueError, "signature mode does not materialize Python rows"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_partition_convergence_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=True,
                validate=False,
            )

    def test_pod_smoke_artifact_records_boundary(self) -> None:
        payload = json.loads(POD_SMOKE.read_text(encoding="utf-8"))

        self.assertEqual(payload["mode"], "partner_cupy_partition_convergence_component_signature_3d")
        self.assertTrue(payload["matches_reference"])
        self.assertEqual(payload["signature"]["contract"], "fixed_radius_graph_component_size_signature_3d")
        self.assertFalse(payload["claim_boundary"]["full_dbscan"])
        self.assertFalse(payload["claim_boundary"]["rt_core_accelerated"])
        metadata = payload["metadata"]
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        self.assertTrue(metadata["graph_component_contract_only"])
        self.assertFalse(metadata["full_dbscan_semantics"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4047RtDbscanPartitionSignatureRuntimeTest(unittest.TestCase):
    def test_candidate_mode_matches_graph_component_reference(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="partner_cupy_partition_convergence_component_signature_3d",
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
        self.assertEqual(metadata["path"], "partner_cupy_partition_convergence_component_signature_3d")
        self.assertTrue(metadata["partition_convergence_hybrid_candidate"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        self.assertTrue(metadata["explicit_candidate_preview"])
        self.assertFalse(metadata["full_dbscan_semantics"])
        self.assertTrue(metadata["graph_component_contract_only"])
        self.assertFalse(metadata["materializes_python_rows"])
        self.assertFalse(metadata["materializes_full_component_labels"])
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
