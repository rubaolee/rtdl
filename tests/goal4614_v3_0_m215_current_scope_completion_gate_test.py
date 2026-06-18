from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.json"
REPORT = ROOT / "docs/reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
APP_AUTHOR_DOC = ROOT / "docs/learn/v3_0_app_author_implementation_strategy.md"


class Goal4614V30M215CurrentScopeCompletionGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module(
            "scripts.goal4614_m215_v3_current_scope_completion_gate"
        )
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_completion_gate_checks_all_pass(self) -> None:
        self.assertEqual("rtdl.v3_0.current_scope_completion.goal4614.v1", self.packet["version"])
        self.assertEqual((), self.packet["failed_checks"])
        for name, passed in self.packet["checks"].items():
            self.assertTrue(passed, name)

    def test_v3_current_scope_is_complete_but_not_public_release(self) -> None:
        scope = self.packet["scope_completion"]
        boundary = self.packet["claim_boundary"]

        self.assertTrue(scope["v3_current_scope_complete"])
        self.assertTrue(scope["benchmark_app_queue_closed"])
        self.assertTrue(scope["v4_deferrals_do_not_block_v3"])
        self.assertFalse(scope["release_tag_authorized"])
        self.assertFalse(scope["public_performance_claim_authorized"])
        self.assertFalse(scope["stable_sdk_authorized"])
        self.assertFalse(scope["true_zero_copy_authorized"])
        self.assertFalse(any(boundary.values()))

    def test_all_apps_are_closed_and_matrix_includes_final_gate(self) -> None:
        rows = {row["app"]: row for row in self.packet["app_rows"]}
        self.assertEqual(10, len(rows))
        self.assertTrue(all(row["queue_class"] == "closed_current_target" for row in rows.values()))
        self.assertTrue(all(not row["pod_needed_next"] for row in rows.values()))
        self.assertEqual(104, self.packet["test_matrix"]["module_count"])
        self.assertEqual(
            "tests.goal4614_v3_0_m215_current_scope_completion_gate_test",
            self.packet["test_matrix"]["last_module"],
        )

    def test_v4_deferrals_are_explicit(self) -> None:
        deferrals = {row["item"] for row in self.packet["v4_deferrals"]}
        self.assertIn("stable_packaged_sdk", deferrals)
        self.assertIn("device_buffer_query_route", deferrals)
        self.assertIn("external_cuda_stream_ordering", deferrals)
        self.assertIn("public_true_zero_copy", deferrals)
        self.assertIn("optix_embree_c_abi_execution", deferrals)
        self.assertIn("device_callable_fusion", deferrals)

    def test_report_index_and_docs_are_wired(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        app_author_doc = APP_AUTHOR_DOC.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4614 / V3 M215", report)
        self.assertIn("Goal4614 V3 current-scope completion gate", index)
        self.assertIn("Goal4614", app_author_doc)
        self.assertIn("V4 deferrals", app_author_doc)


if __name__ == "__main__":
    unittest.main()
