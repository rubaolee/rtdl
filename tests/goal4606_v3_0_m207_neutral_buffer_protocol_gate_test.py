from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4606_v3_0_m207_neutral_buffer_protocol_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4606_v3_0_m207_neutral_buffer_protocol_gate_2026-06-17.md"
MATRIX_DOC = ROOT / "docs/learn/v3_0_binding_and_device_interop_matrix.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4606V30M207NeutralBufferProtocolGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4606_m207_v3_neutral_buffer_protocol_gate")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_neutral_buffer_protocol_gate_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.neutral_buffer_protocol_gate.goal4606.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_protocol_descriptors_have_expected_statuses(self) -> None:
        descriptors = self.checked_in["descriptors"]
        self.assertEqual("cupy", descriptors["cupy_priority"]["buffer"]["source_protocol"])
        self.assertEqual("dlpack", descriptors["dlpack"]["buffer"]["source_protocol"])
        self.assertEqual("cuda_array_interface", descriptors["cuda_array_interface"]["buffer"]["source_protocol"])
        self.assertEqual("array_interface", descriptors["array_interface"]["buffer"]["source_protocol"])
        self.assertEqual(
            "borrowed_device_pointer_unmeasured",
            descriptors["dlpack"]["transfer_status"],
        )
        self.assertTrue(descriptors["measured_zero_copy_candidate"]["zero_copy_claim_authorized"])
        self.assertFalse(descriptors["measured_zero_copy_candidate"]["public_speedup_claim_authorized"])

    def test_docs_report_and_index_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4606 / V3 M207", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4606 neutral buffer protocol gate", INDEX.read_text(encoding="utf-8"))
        doc = MATRIX_DOC.read_text(encoding="utf-8")
        self.assertIn("Validated protocol classification/descriptor gate", doc)
        self.assertIn("No implemented C ABI DLPack adapter", doc)

    def test_boundaries_remain_descriptor_only(self) -> None:
        matrix = self.checked_in["status_matrix"]
        self.assertEqual("validated_descriptor_only", matrix["dlpack_descriptor_path"])
        self.assertEqual("blocked", matrix["c_abi_dlpack_adapter"])
        self.assertEqual("blocked", matrix["device_buffer_query_route"])
        self.assertEqual("blocked", matrix["public_true_zero_copy_claim"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key.endswith("_authorized") and key not in {
                "neutral_buffer_protocol_gate_authorized",
                "dlpack_descriptor_metadata_authorized",
                "cuda_array_interface_descriptor_metadata_authorized",
                "host_array_interface_descriptor_authorized",
                "lifetime_state_machine_authorized",
            }:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
