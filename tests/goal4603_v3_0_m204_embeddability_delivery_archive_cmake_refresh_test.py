from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4603_v3_0_m204_embeddability_delivery_archive_cmake_refresh_2026-06-17.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4603V30M204EmbeddabilityDeliveryArchiveCmakeRefreshTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4603_m204_v3_embeddability_delivery_archive_cmake_refresh"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_delivery_archive_cmake_refresh_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.embeddability_delivery_archive_cmake.goal4603.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_status_matrix_includes_archive_cmake_and_keeps_blocks(self) -> None:
        matrix = self.packet["status_matrix"]
        self.assertEqual("validated_imported_target", matrix["prefix_cmake_find_package"])
        self.assertEqual("validated_extracted_archive_imported_target", matrix["archive_cmake_find_package"])
        self.assertEqual("validated_pkg_config_and_cmake", matrix["source_tree_and_prefix_stage_handoff"])
        self.assertEqual("blocked", matrix["device_buffer_query_route"])
        self.assertEqual("blocked", matrix["dlpack_zero_copy"])
        self.assertEqual("blocked_until_1_0_gates", matrix["stable_abi"])
        self.assertEqual("blocked", matrix["release"])

    def test_architecture_doc_is_current_to_goal4608(self) -> None:
        text = ARCHITECTURE_DOC.read_text(encoding="utf-8")
        self.assertIn("As of Goal4608", text)
        self.assertIn("Extracted source-tree stage archive CMake consumer proof", text)
        self.assertIn("Archive-stage Python `ctypes` smoke", text)
        self.assertIn("staged-prefix/archive consumption", text)
        self.assertIn("proof, not an installed SDK promise", text)
        self.assertIn("not an installed SDK", text)

    def test_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4603 / V3 M204", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4603 embeddability delivery archive CMake refresh", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["archive_cmake_stage_authorized"])
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
