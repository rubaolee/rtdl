from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4612_v3_0_m213_c_abi_last_error_staged_example_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4612_v3_0_m213_c_abi_last_error_staged_example_2026-06-17.md"
EXAMPLE = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/c_api_last_error_client.c"
STAGING_CONTRACT = ROOT / "docs/history/v4_preparatory_embedding/v3_0_c_abi_staging_contract.md"
EMBEDDING_README = ROOT / "docs/history/v4_preparatory_embedding/examples/embedding/README.md"
BINDING_MATRIX = ROOT / "docs/history/v4_preparatory_embedding/v3_0_binding_and_device_interop_matrix.md"
ARCHITECTURE_DOC = ROOT / "docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"


class Goal4612V30M213CAbiLastErrorStagedExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4612_m213_v3_c_abi_last_error_staged_example")
        cls.packet = cls.module.build_packet(ROOT, run_smoke=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_last_error_staged_example_static_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_last_error_staged_example.goal4612.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_staged_example_smoke_passed(self) -> None:
        smoke = self.checked_in["staged_example_smoke"]
        self.assertTrue(smoke["ok"])
        self.assertTrue(smoke["make_result"]["ok"])
        self.assertTrue(smoke["compile_result"]["ok"])
        self.assertTrue(smoke["run_result"]["ok"])
        self.assertIn("validated_last_error_diagnostics_cases=7", smoke["run_result"]["stdout"])

    def test_docs_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("rtdl_context_last_error", EXAMPLE.read_text(encoding="utf-8"))
        self.assertIn("examples/c_api_last_error_client.c", STAGING_CONTRACT.read_text(encoding="utf-8"))
        self.assertIn("c_api_last_error_client.c", EMBEDDING_README.read_text(encoding="utf-8"))
        self.assertIn("staged `c_api_last_error_client.c` example", BINDING_MATRIX.read_text(encoding="utf-8"))
        self.assertIn("As of Goal4612", ARCHITECTURE_DOC.read_text(encoding="utf-8"))
        self.assertIn("Goal4612 / V3 M213", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4612 C ABI last-error staged example", INDEX.read_text(encoding="utf-8"))
        self.assertTrue(self.checked_in["claim_boundary"]["last_error_staged_example_authorized"])
        for key, value in self.checked_in["claim_boundary"].items():
            if key != "last_error_staged_example_authorized":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
