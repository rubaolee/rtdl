from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples.current.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact,
)
from examples.current.research_benchmarks.librts_spatial_index import (
    rtdl_librts_spatial_index_benchmark_app as librts,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3808_remaining_low_risk_alias_cleanup_2026-06-07.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
LIBRTS_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "librts_spatial_index"
    / "rtdl_librts_spatial_index_benchmark_app.py"
)


class Goal3808RemainingLowRiskAliasCleanupTest(unittest.TestCase):
    def test_contact_current_descriptor_alias_preserves_generic_protocol(self) -> None:
        current = contact.describe_bounded_witness_session(
            backend="optix",
            candidate_row_count=17,
            witness_capacity=9,
        )
        legacy = contact.describe_v2_4_bounded_witness_session(
            backend="optix",
            candidate_row_count=17,
            witness_capacity=9,
        )

        self.assertEqual(current["current_helper"], "describe_bounded_witness_session")
        self.assertEqual(
            current["legacy_helper_alias"],
            "describe_v2_4_bounded_witness_session",
        )
        self.assertEqual(current["v2_4_protocol_version"], rt.V2_4_PARTNER_PROTOCOL_VERSION)
        self.assertEqual(current["primitive"], legacy["primitive"])
        self.assertEqual(current["native_symbols"], legacy["native_symbols"])
        self.assertEqual(current["row_schema"], contact.ROW_SCHEMA)
        self.assertTrue(current["descriptor_only"])
        self.assertFalse(current["app_specific_native_vocab_allowed"])
        native_vocab = " ".join((current["primitive"], *current["native_symbols"])).lower()
        self.assertNotIn("contact", native_vocab)
        self.assertNotIn("collision", native_vocab)

    def test_librts_current_plan_alias_preserves_primitive_first_contract(self) -> None:
        current = librts.primitive_first_plan_payload()
        legacy = librts.v2_5_plan_payload()

        self.assertEqual(current["mode"], "primitive_first_plan")
        self.assertEqual(current["current_helper"], "primitive_first_plan_payload")
        self.assertEqual(current["legacy_helper_alias"], "v2_5_plan_payload")
        self.assertEqual(
            current["v2_5_primitive_first_plan"],
            legacy["v2_5_primitive_first_plan"],
        )
        plan = current["v2_5_primitive_first_plan"]
        boundary = current["claim_boundary"]
        self.assertEqual(plan["selected_path"], "prepared_generic_aabb_index_query_2d")
        self.assertEqual(plan["selected_primitives"], ("AABB_INDEX_QUERY_2D",))
        self.assertFalse(plan["typed_hit_stream_forced"])
        self.assertFalse(plan["partner_continuation_required"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_authorized"])
        self.assertFalse(boundary["triton_speedup_claim_authorized"])
        self.assertTrue(boundary["primitive_first_plan_only"])

    def test_librts_cli_current_plan_mode_is_available(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(LIBRTS_APP), "--mode", "primitive_first_plan"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["mode"], "primitive_first_plan")
        self.assertEqual(payload["current_helper"], "primitive_first_plan_payload")
        self.assertEqual(payload["legacy_helper_alias"], "v2_5_plan_payload")
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_authorized"])

    def test_report_and_todo_record_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3808",
            "describe_bounded_witness_session",
            "primitive_first_plan_payload",
            "No native engine code changed",
            "No old compatibility helper was removed",
            "Historical protocol names and artifact keys remain stable",
        ):
            self.assertIn(phrase, text)
        todo = TODO.read_text(encoding="utf-8")
        self.assertIn("Goal3808 cleaned the two remaining low-risk app-facing candidates", todo)
        self.assertIn("RayJoin topology-reference helper remains intentionally versioned", todo)


if __name__ == "__main__":
    unittest.main()
