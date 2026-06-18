from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4601_v3_0_m202_embeddability_delivery_status_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4601_v3_0_m202_embeddability_delivery_status_refresh_2026-06-17.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4601V30M202EmbeddabilityDeliveryStatusRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4601_m202_v3_embeddability_delivery_status_refresh")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_delivery_status_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_delivery_status.goal4601.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_separates_ready_slice_from_blocked_slice(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated_imported_target", matrix["prefix_cmake_find_package"])
        self.assertEqual("validated_lifecycle_host_aabb2_cuda_metadata", matrix["python_ctypes_prefix_examples"])
        self.assertEqual("validated_sizeof_offsetof_matches", matrix["python_ctypes_c_layout_audit"])
        self.assertEqual("blocked", matrix["device_buffer_query_route"])
        self.assertEqual("blocked", matrix["dlpack_zero_copy"])
        self.assertEqual("blocked_until_1_0_gates", matrix["stable_abi"])
        self.assertEqual("blocked", matrix["release"])

    def test_architecture_doc_is_current_at_or_beyond_goal4600(self) -> None:
        text = ARCHITECTURE_DOC.read_text(encoding="utf-8")
        self.assertIn("As of Goal4610", text)
        self.assertIn("find_package(rtdl-c-api CONFIG REQUIRED)", text)
        self.assertIn("`rtdl::c_api`", text)
        self.assertIn("C/Python `ctypes` layout audit", text)
        self.assertIn("not an installed SDK", text)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4601 / V3 M202", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4601 embeddability delivery status refresh", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["cmake_prefix_stage_consumption_authorized"])
        self.assertTrue(self.checked_in["claim_boundary"]["python_ctypes_layout_drift_check_authorized"])
        for key in (
            "system_install_authorized",
            "packaged_sdk_authorized",
            "stable_abi_authorized",
            "dlpack_zero_copy_authorized",
            "device_buffer_query_route_authorized",
            "optix_embree_c_abi_query_authorized",
            "generated_language_binding_authorized",
            "release_authorized",
        ):
            self.assertFalse(self.checked_in["claim_boundary"][key], key)


if __name__ == "__main__":
    unittest.main()
