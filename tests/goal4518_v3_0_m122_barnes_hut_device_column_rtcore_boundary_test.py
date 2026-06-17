from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4518_v3_0_m122_barnes_hut_device_column_rtcore_boundary_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
RT_MATRIX = ROOT / "docs/learn/rt_core_evidence_matrix.md"
README = ROOT / "examples/current/research_benchmarks/barnes_hut/README.md"
ROUTE_SOURCE = ROOT / "src/rtdsl/current_benchmark_route_decisions.py"
ADEQUACY_SOURCE = ROOT / "src/rtdsl/current_benchmark_adequacy.py"
SCRIPT = ROOT / "scripts/goal4518_m122_barnes_hut_device_column_rtcore_boundary.py"


class Goal4518V30M122BarnesHutDeviceColumnRtcoreBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.audit = cls.packet["aggregate_frontier_device_column_audit"]

    def test_source_audit_blocks_rtcore_claim_for_current_device_column_path(self) -> None:
        self.assertEqual(
            "rtdl.v3_0.barnes_hut_device_column_rtcore_boundary.goal4518.v1",
            self.packet["version"],
        )
        self.assertTrue(self.audit["contains_runtime_cuda_kernel_source"])
        self.assertTrue(self.audit["contains_cu_module_load"])
        self.assertTrue(self.audit["contains_cu_launch_kernel"])
        self.assertFalse(self.audit["contains_optix_launch"])
        self.assertFalse(self.audit["contains_optix_trace"])
        self.assertFalse(self.audit["rt_core_traversal_claim_authorized"])
        self.assertEqual(
            "cuda_driver_runtime_compiled_cubin_inside_optix_backend",
            self.audit["implementation_vehicle"],
        )

    def test_fused_contract_requires_optix_traversal_proof_for_rtcore_wording(self) -> None:
        contract = rt.validate_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_contract()
        requirements = " ".join(contract["rt_core_claim_requirements"]).lower()
        self.assertIn("optix pipeline", requirements)
        self.assertIn("optixtrace", requirements)
        self.assertIn("cuda-only fused implementation", requirements)
        self.assertIn(
            "CUDA-only fused implementation may be useful device evidence but not RT-core evidence",
            contract["rt_core_claim_requirements"],
        )

    def test_live_guidance_replaces_stale_rtcore_device_column_wording(self) -> None:
        route = ROUTE_SOURCE.read_text(encoding="utf-8")
        adequacy = ADEQUACY_SOURCE.read_text(encoding="utf-8")
        docs = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (INDEX, MATRIX, RT_MATRIX, README)
        )
        self.assertTrue(self.packet["live_guidance"]["route_guidance_uses_cuda_device_column_wording"])
        self.assertTrue(self.packet["live_guidance"]["adequacy_uses_cuda_device_column_wording"])
        self.assertFalse(self.packet["live_guidance"]["route_guidance_stale_rtcore_device_column_wording"])
        self.assertFalse(self.packet["live_guidance"]["adequacy_stale_rtcore_device_column_wording"])
        for text in (route, adequacy, docs):
            self.assertIn("OptiX-library CUDA device-column evidence", text)
        self.assertNotIn("RT-core device-column evidence", route)
        self.assertNotIn("RT-core aggregate-frontier device-column", route)
        self.assertNotIn("RT-core device-column evidence", adequacy)
        self.assertNotIn("RT-core aggregate-frontier device-column", adequacy)

    def test_report_docs_and_script_are_present(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Goal4518 / V3 M122", report)
        self.assertIn("not current RT-core traversal evidence", report)
        self.assertIn("Goal4518 Barnes-Hut device-column RT-core boundary audit", index)
        self.assertIn("Goal4518 audits the current prepared aggregate-frontier device-column", readme)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
