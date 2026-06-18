from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4578_v3_0_m179_c_abi_capability_queries_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4578_v3_0_m179_c_abi_capability_queries_2026-06-17.md"
MANIFEST = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_symbol_manifest_v0_1_3.json"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4578V30M179CAbiCapabilityQueriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4578_m179_v3_c_abi_capability_queries")
        cls.packet = cls.module.build_packet(ROOT, run_runtime=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_capability_query_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_capability_queries.goal4578.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_smoke_checks_capabilities(self) -> None:
        runtime = self.checked_in["runtime_build"]
        self.assertTrue(runtime["ok"])
        checks = runtime["ctypes_smoke"]["checks"]
        self.assertTrue(checks["auto_backend_is_supported"])
        self.assertTrue(checks["cpu_backend_is_supported"])
        self.assertTrue(checks["optix_backend_is_not_supported"])
        self.assertTrue(checks["host_aabb2_overlap_route_is_supported"])
        self.assertTrue(checks["cuda_aabb2_overlap_route_is_not_supported"])
        self.assertTrue(checks["host_segment_ray_route_is_not_supported"])

    def test_manifest_report_index_and_boundaries_are_wired(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("rtdl_backend_is_supported", manifest["symbols"])
        self.assertIn("rtdl_route_is_supported", manifest["symbols"])
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4578 / V3 M179", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4578 C ABI capability queries", INDEX.read_text(encoding="utf-8"))
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
