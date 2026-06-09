from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (
    run_rt_dbscan_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal4065_rt_dbscan_prepared_partition_signature_app_mode_2026-06-09.md"


def _cupy_available() -> bool:
    return importlib.util.find_spec("cupy") is not None


class Goal4065RtDbscanPreparedPartitionSignatureSourceTest(unittest.TestCase):
    def test_app_and_docs_expose_prepared_candidate_mode(self) -> None:
        text = APP.read_text(encoding="utf-8") + "\n" + README.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")

        for fragment in (
            "partner_cupy_prepared_partition_convergence_component_signature_3d",
            "prepare_v2_8_fixed_radius_partition_convergence_summary_cupy_preview_3d",
            "run_v2_8_fixed_radius_partition_convergence_component_signature_cupy_prepared_preview_3d",
            "prepared_partition_summary_app_mode",
            "prepared_partition_summary_sec",
            "component_signature_sec",
            "graph_component_contract_only",
            "full_dbscan_semantics",
        ):
            self.assertIn(fragment, text)

    def test_prepared_signature_mode_rejects_python_rows_before_cupy_is_needed(self) -> None:
        with self.assertRaisesRegex(ValueError, "signature mode does not materialize Python rows"):
            run_rt_dbscan_benchmark(
                mode="partner_cupy_prepared_partition_convergence_component_signature_3d",
                dataset="tiny",
                point_count=None,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=True,
                validate=False,
            )


@unittest.skipUnless(_cupy_available(), "CuPy is not available in this environment")
class Goal4065RtDbscanPreparedPartitionSignatureRuntimeTest(unittest.TestCase):
    def test_prepared_candidate_mode_matches_graph_component_reference(self) -> None:
        payload = run_rt_dbscan_benchmark(
            mode="partner_cupy_prepared_partition_convergence_component_signature_3d",
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
        self.assertEqual(metadata["path"], "partner_cupy_prepared_partition_convergence_component_signature_3d")
        self.assertTrue(metadata["prepared_partition_summary_app_mode"])
        self.assertTrue(metadata["prepared_partition_summary_reused"])
        self.assertTrue(metadata["partition_convergence_hybrid_candidate"])
        self.assertFalse(metadata["partition_convergence_hybrid_promoted"])
        self.assertFalse(metadata["current_default_route"])
        self.assertFalse(metadata["full_dbscan_semantics"])
        self.assertTrue(metadata["graph_component_contract_only"])
        self.assertFalse(metadata["materializes_python_rows"])
        self.assertFalse(metadata["materializes_full_component_labels"])
        self.assertFalse(metadata["rt_core_accelerated"])
        self.assertFalse(metadata["release_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
