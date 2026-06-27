import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_barnes_hut_vector_accumulation_contract.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixBarnesHutVectorAccumulationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_contract_candidate_not_m7(self):
        payload = self.payload
        self.assertEqual(payload["status"], "barnes_hut_vector_accumulation_contract_candidate_not_m7")
        self.assertEqual(payload["generic_capability"], "vector_accumulation")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_m6_evidence_is_negative_for_current_prepared_optix_shape(self):
        evidence = self.payload["m6_route_parity_evidence"]
        self.assertEqual(evidence["overall_status"], "internal_m6_route_parity_evidence")
        self.assertTrue(evidence["timing_basis_mixed"])
        self.assertEqual(
            evidence["fastest_by_scale"],
            {
                "32768": "numba_cuda_fused",
                "65536": "numba_cuda_fused",
                "131072": "numba_cuda_fused",
            },
        )
        self.assertAlmostEqual(evidence["prepared_optix_numba_over_fastest"]["32768"], 7.328211765388345)
        self.assertAlmostEqual(evidence["prepared_optix_numba_over_fastest"]["65536"], 5.120049883650066)
        self.assertAlmostEqual(evidence["prepared_optix_numba_over_fastest"]["131072"], 13.91167731446378)
        self.assertIn("negative for the current prepared RTDL/OptiX frontier-emission shape", evidence["reading"])

    def test_required_contract_is_generic_executable_and_not_rt_core_claim(self):
        contract = self.payload["required_generic_contract"]
        self.assertEqual(
            contract["contract"],
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
        )
        self.assertEqual(contract["status"], "implemented_cuda_device_accumulation_not_rt_core")
        self.assertTrue(contract["executable"])
        self.assertEqual(contract["required_first_backend"], "optix")
        self.assertIn("vector_x:float64[source_count]", contract["output_device_columns"])
        self.assertIn("aggregate-frontier row emission", contract["must_avoid"])
        self.assertIn("app-specific native engine callbacks", contract["must_avoid"])
        self.assertIn("optixTrace", " ".join(contract["rt_core_claim_requirements"]))
        self.assertTrue(contract["claim_boundary"]["runtime_implemented"])
        for key, value in contract["claim_boundary"].items():
            if key == "runtime_implemented":
                continue
            self.assertFalse(value, key)

    def test_markdown_records_boundary_requirements_and_decision_audit(self):
        for phrase in (
            "M7 rows added by this packet: 0",
            "Apps are evidence harnesses only",
            "generic_aggregate_tree_fused_weighted_vector_sum_2d_rt_native_v1",
            "implemented_cuda_device_accumulation_not_rt_core",
            "prepared RTDL/OptiX+Numba over fastest",
            "Do not publish Barnes-Hut RT-core speedup",
            "Do not call fused Numba CUDA an RT-core result.",
            "claude_cli_blocked_not_closed",
            "not_closed_requires_external_review_before_m7",
            "call_for_review_phoenix_v3_barnes_hut_vector_accumulation_contract_2026-06-21.md",
            "Was I foolish?",
            "the honest V3 move is to define the missing reusable primitive",
        ):
            self.assertIn(phrase, self.text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["m6_route_parity_evidence"], self.payload["m6_route_parity_evidence"])
            self.assertEqual(
                rebuilt["required_generic_contract"]["status"],
                "implemented_cuda_device_accumulation_not_rt_core",
            )
            self.assertIn("Barnes-Hut Vector-Accumulation Contract", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
