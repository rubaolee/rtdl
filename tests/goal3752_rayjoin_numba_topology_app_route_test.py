from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from examples.benchmark_apps.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/benchmark_apps/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py"
REPORT = ROOT / "docs/reports/goal3752_rayjoin_numba_topology_app_route_2026-06-07.md"
A5000_ARTIFACT = ROOT / "docs/reports/goal3752_rayjoin_numba_topology_app_route_a5000.json"
README = ROOT / "examples/benchmark_apps/spatial_rayjoin/README.md"


class Goal3752RayjoinNumbaTopologyAppRouteTest(unittest.TestCase):
    def test_route_is_exposed_from_the_rayjoin_cli_app(self) -> None:
        text = APP.read_text(encoding="utf-8")
        self.assertIn("run_rayjoin_v2_9_numba_side_aware_topology_reference", text)
        self.assertIn('"v2_9_numba_side_aware_topology_reference"', text)
        self.assertIn("filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba", text)
        self.assertIn("chains_to_topology_rows", text)

    def test_report_records_user_facing_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3752", text)
        self.assertIn("app-facing route", text)
        self.assertIn("no-RawKernel", text)
        self.assertIn("does not authorize", text)

    def test_spatial_rayjoin_readme_documents_numba_topology_route(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("v2_9_numba_side_aware_topology_reference", text)
        self.assertIn("filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba", text)
        self.assertIn("not a RayJoin paper", text)

    def test_a5000_artifact_records_fixture_execution_boundary(self) -> None:
        payload = json.loads(A5000_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["execution_route"], "v2_9_numba_side_aware_topology_reference")
        self.assertEqual(payload["partner_reference"]["partner"], "numba")
        self.assertTrue(payload["summary"]["parity_vs_python_columns"])
        self.assertEqual(payload["summary"]["candidate_count"], 3)
        self.assertFalse(any(payload["claim_boundary"].values()))
        self.assertFalse(payload["partner_reference"]["raw_cuda_kernel_required"])

    def test_route_executes_when_numba_cuda_is_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        payload = app.run_rayjoin_v2_9_numba_side_aware_topology_reference(
            limit_chains=3,
            include_rows=False,
        )
        self.assertEqual(payload["execution_route"], "v2_9_numba_side_aware_topology_reference")
        self.assertEqual(payload["partner_reference"]["partner"], "numba")
        self.assertFalse(any(payload["claim_boundary"].values()))
        self.assertTrue(payload["summary"]["parity_vs_python_columns"])
        self.assertEqual(payload["summary"]["candidate_count"], 3)
        self.assertEqual(payload["summary"]["numba_row_count"], payload["summary"]["python_reference_row_count"])


if __name__ == "__main__":
    unittest.main()
