from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4610_v3_0_m211_c_abi_independent_context_concurrency_smoke_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4610_v3_0_m211_c_abi_independent_context_concurrency_smoke_2026-06-17.md"
OWNERSHIP_DOC = ROOT / "docs/learn/v3_0_c_abi_ownership_threading_contract.md"
ARCHITECTURE_DOC = ROOT / "docs/learn/v3_0_embeddability_architecture_strategy.md"
BINDING_MATRIX = ROOT / "docs/learn/v3_0_binding_and_device_interop_matrix.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4610V30M211CAbiIndependentContextConcurrencySmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4610_m211_v3_c_abi_independent_context_concurrency_smoke")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_independent_context_concurrency_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_independent_context_concurrency.goal4610.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_concurrency_smoke_passed(self) -> None:
        smoke = self.checked_in["concurrency_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["shared_library"]["ok"])
        self.assertTrue(smoke["client_compile"]["ok"])
        self.assertTrue(smoke["client_run"]["ok"])
        self.assertEqual(
            "validated_independent_context_threads=8 iterations=64",
            smoke["client_run"]["stdout"],
        )

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4610 / V3 M211", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4610 C ABI independent-context concurrency smoke", INDEX.read_text(encoding="utf-8"))
        self.assertIn("Goal4610", OWNERSHIP_DOC.read_text(encoding="utf-8"))
        self.assertIn("As of Goal4610", ARCHITECTURE_DOC.read_text(encoding="utf-8"))
        self.assertIn("Independent-context host-route concurrency", BINDING_MATRIX.read_text(encoding="utf-8"))
        matrix = self.checked_in["support_matrix"]
        self.assertEqual("validated_source_tree_smoke", matrix["independent_context_host_aabb2_concurrency"])
        self.assertEqual("blocked", matrix["stable_thread_safety_wording"])
        self.assertTrue(
            self.checked_in["claim_boundary"]["independent_context_host_route_concurrency_authorized"]
        )
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "independent_context_host_route_concurrency_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
