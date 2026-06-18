from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4573_v3_0_m174_c_abi_backend_runtime_fail_closed_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
C_ABI_DOC = ROOT / "docs/learn/v3_0_c_abi_draft.md"


class Goal4573V30M174CAbiBackendRuntimeFailClosedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4573_m174_v3_c_abi_backend_runtime_fail_closed")
        cls.packet = cls.module.build_packet(ROOT, run_compile=False)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_static_backend_runtime_checks_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.c_abi_backend_runtime_fail_closed.goal4573.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_checked_in_runtime_validated_fail_closed_cases(self) -> None:
        self.assertTrue(self.checked_in["checks"]["shared_library_build_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_compile_ok"])
        self.assertTrue(self.checked_in["checks"]["c_client_run_ok"])
        self.assertTrue(self.checked_in["checks"]["runtime_validated_all_cases"])
        for name, passed in self.checked_in["validated_cases"].items():
            self.assertTrue(passed, name)
        stdout = self.checked_in["client_result"]["client_run"]["stdout"]
        self.assertIn("validated_backend_runtime_cases=5", stdout)

    def test_doc_report_index_and_boundaries_are_wired(self) -> None:
        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4573 / V3 M174", REPORT.read_text(encoding="utf-8"))
        self.assertIn("Goal4573 C ABI backend/runtime fail-closed", INDEX.read_text(encoding="utf-8"))
        doc = C_ABI_DOC.read_text(encoding="utf-8")
        self.assertIn("Other backend requests", doc)
        self.assertIn("non-host runtime", doc)
        self.assertIn("external stream adoption", doc)
        for key, value in self.checked_in["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
