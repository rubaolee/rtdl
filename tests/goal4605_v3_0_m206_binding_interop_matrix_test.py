from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4605_v3_0_m206_binding_device_interop_matrix_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4605_v3_0_m206_binding_device_interop_matrix_2026-06-17.md"
MATRIX_DOC = ROOT / "docs/learn/v3_0_binding_and_device_interop_matrix.md"
LEARN_README = ROOT / "docs/learn/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4605V30M206BindingInteropMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4605_m206_v3_binding_interop_matrix")
        cls.packet = cls.module.build_packet(ROOT, run_live_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_binding_interop_matrix_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.binding_device_interop_matrix.goal4605.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_pod_live_smokes_pass(self) -> None:
        smokes = self.checked_in["live_smokes"]
        self.assertTrue(smokes["host_external_runtime"]["ok"])
        self.assertTrue(smokes["cuda_buffer_metadata"]["ok"])
        self.assertTrue(smokes["python_cuda_metadata_bridge"]["ok"])
        self.assertEqual(
            "python_ctypes_cuda_metadata_shape=(3,4) query_route_rejected=invalid argument",
            smokes["python_cuda_metadata_bridge"]["stdout"],
        )

    def test_docs_index_and_report_are_wired(self) -> None:
        doc = MATRIX_DOC.read_text(encoding="utf-8")
        self.assertIn("CUDA descriptor metadata", doc)
        self.assertIn("Do not say DLPack support", doc)
        self.assertIn("V3.0 Binding And Device Interop Matrix", LEARN_README.read_text(encoding="utf-8"))
        self.assertIn("Goal4605 / V3 M206", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4605 binding/device interop matrix", INDEX.read_text(encoding="utf-8"))

    def test_status_matrix_and_boundaries_are_explicit(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        matrix = self.checked_in["status_matrix"]
        self.assertEqual("validated_metadata_only", matrix["cuda_buffer_descriptor_import_export"])
        self.assertEqual("validated_metadata_only", matrix["cuda_array_interface_to_c_abi_descriptor"])
        self.assertEqual("rejected_invalid_argument", matrix["cuda_descriptor_host_aabb2_query_route"])
        self.assertEqual("design_contract_only", matrix["dlpack"])
        self.assertEqual("blocked", matrix["device_buffer_query_route"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key.endswith("_authorized") and key not in {
                "source_tree_c_handoff_authorized",
                "pkg_config_stage_handoff_authorized",
                "cmake_stage_handoff_authorized",
                "python_ctypes_examples_authorized",
                "host_aabb2_c_abi_query_authorized",
                "cuda_metadata_descriptor_authorized",
                "cuda_array_interface_metadata_bridge_authorized",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
