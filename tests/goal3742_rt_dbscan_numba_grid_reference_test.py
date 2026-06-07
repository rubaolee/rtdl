from __future__ import annotations

from pathlib import Path
import os
import unittest

import rtdsl as rt
from rtdsl import partner as rtdl_partner
from examples.v2_0.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/v2_0/research_benchmarks/rt_dbscan/rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples/v2_0/research_benchmarks/rt_dbscan/README.md"
REPORT = ROOT / "docs/reports/goal3742_rt_dbscan_numba_grid_reference_2026-06-07.md"


def _run_tiny(mode: str) -> dict[str, object]:
    return app.run_rt_dbscan_benchmark(
        mode=mode,
        dataset="tiny",
        point_count=None,
        radius=None,
        min_neighbors=None,
        seed=20260519,
        partner="cupy",
        include_rows=False,
        validate=True,
    )


class Goal3742RtDbscanNumbaGridReferenceTest(unittest.TestCase):
    def test_numba_radius_graph_component_surface_is_exported(self) -> None:
        self.assertTrue(hasattr(rt, "PreparedNumbaRadiusGraphComponents3DGrid"))
        self.assertTrue(hasattr(rt, "prepare_radius_graph_components_3d_numba_grid_partner_columns"))
        self.assertTrue(hasattr(rt, "radius_graph_components_3d_numba_grid_partner_columns"))
        self.assertTrue(hasattr(rt, "radius_graph_components_3d_numba_prepared_grid_partner_columns"))
        self.assertIn("cuda_array_interface", rtdl_partner.registered())

    def test_rt_dbscan_app_exposes_explicit_numba_modes(self) -> None:
        text = APP.read_text(encoding="utf-8")
        self.assertIn("partner_numba_grid_components_3d", text)
        self.assertIn("partner_numba_prepared_grid_components_3d", text)
        self.assertIn("optix_rt_core_flags_numba_prepared_grid_components_3d", text)
        self.assertIn('point_rows_to_partner_columns(points, partner="numba")', text)
        self.assertIn('partner="numba"', text)
        self.assertIn("raw_cuda_kernel_required", text)

    def test_readme_documents_numba_as_reference_not_rt_claim(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("partner_numba_grid_components_3d", text)
        self.assertIn("does not require users to write CuPy", text)
        self.assertIn("claim RT-core acceleration", text)
        self.assertIn("host-prepared", text)

    def test_report_records_pod_evidence_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3742", text)
        self.assertIn("A5000 pod validation", text)
        self.assertIn("Numba / CuPy", text)
        self.assertIn("does not authorize", text)
        self.assertIn("app-specific native-engine logic", text)

    def test_numba_grid_matches_tiny_cpu_signature_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        cpu = _run_tiny("cpu_reference")
        numba = _run_tiny("partner_numba_grid_components_3d")
        self.assertTrue(numba["matches_reference"])
        self.assertEqual(numba["signature"], cpu["signature"])
        self.assertEqual(numba["metadata"]["partner"], "numba")
        self.assertEqual(
            numba["metadata"]["partner_reference_contract"],
            "generic_numba_grid_radius_graph_component_labels_3d",
        )
        self.assertFalse(numba["metadata"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(numba["metadata"]["whole_app_speedup_claim_authorized"])

    def test_numba_prepared_grid_matches_tiny_cpu_signature_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        cpu = _run_tiny("cpu_reference")
        numba = _run_tiny("partner_numba_prepared_grid_components_3d")
        self.assertTrue(numba["matches_reference"])
        self.assertEqual(numba["signature"], cpu["signature"])
        self.assertEqual(
            numba["metadata"]["partner_reference_contract"],
            "generic_prepared_numba_grid_radius_graph_component_labels_3d",
        )
        self.assertTrue(numba["metadata"]["host_prepared_grid_index_used"])
        self.assertTrue(numba["metadata"]["device_grid_labeling_used"])
        self.assertFalse(numba["metadata"]["rt_core_speedup_claim_authorized"])

    def test_optix_count_threshold_can_feed_numba_grid_when_cuda_and_optix_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        optix_library = os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB")
        if not optix_library:
            candidate = ROOT / "build/librtdl_optix.so"
            if candidate.exists():
                os.environ["RTDL_OPTIX_LIBRARY"] = str(candidate)
            else:
                self.skipTest("OptiX library is not available in this environment")
        cpu = _run_tiny("cpu_reference")
        payload = _run_tiny("optix_rt_core_flags_numba_prepared_grid_components_3d")
        self.assertTrue(payload["matches_reference"])
        self.assertEqual(payload["signature"], cpu["signature"])
        self.assertEqual(payload["metadata"]["partner"], "numba")
        self.assertTrue(payload["metadata"]["optix_backend_used"])
        self.assertTrue(payload["metadata"]["rt_core_accelerated"])
        self.assertEqual(
            payload["metadata"]["threshold_metadata"]["partner"],
            "numba",
        )
        self.assertFalse(payload["metadata"]["rt_core_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
