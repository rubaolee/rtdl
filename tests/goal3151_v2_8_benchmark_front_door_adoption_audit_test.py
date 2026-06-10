from __future__ import annotations

from pathlib import Path
from unittest import mock
import unittest

import rtdsl as rt
from examples.current.research_benchmarks.spatial_rayjoin import (
    rtdl_rayjoin_v2_spatial_join_app as rayjoin,
)
from examples.current.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3151_v2_8_benchmark_front_door_adoption_audit_2026-06-03.md"
HANDOFF = (
    ROOT
    / "docs"
    / "handoff"
    / "HANDOFF_EXTERNAL_REVIEW_GOAL3151_V2_8_BENCHMARK_FRONT_DOOR_ADOPTION_2026-06-03.md"
)
RAYJOIN_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
TRIANGLE_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "triangle_counting"
    / "rtdl_triangle_counting_benchmark_app.py"
)


class Goal3151BenchmarkFrontDoorAdoptionAuditTest(unittest.TestCase):
    def test_report_classifies_all_promoted_benchmark_apps(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for app in rt.V2_8_PROMOTED_BENCHMARK_APPS:
            self.assertEqual(text.count(f"| `{app}` |"), 1, app)
        self.assertIn("audit_complete_with_two_safe_migrations", text)
        self.assertIn("No safe migration in this goal", text)
        self.assertIn(str(HANDOFF.relative_to(ROOT)).replace("\\", "/"), text)

    def test_safe_migrations_preserve_legacy_aliases_and_use_v2_8_front_door(self) -> None:
        rayjoin_source = RAYJOIN_APP.read_text(encoding="utf-8")
        triangle_source = TRIANGLE_APP.read_text(encoding="utf-8")

        for source, legacy_function in (
            (rayjoin_source, "run_rayjoin_v2_6_numba_compact_mask_preview"),
            (triangle_source, "run_triangle_counting_v2_6_numba_compact_mask_preview"),
        ):
            self.assertIn(legacy_function, source)
            self.assertIn("execute_compact_mask_typed_stream_partner_columns", source)
            self.assertIn("v2_8_segmented_typed_stream_front_door_used", source)
            self.assertNotIn("rt.run_numba_compact_mask_i64(", source)

    def test_plan_payloads_advertise_v2_8_front_door_without_promoting_claims(self) -> None:
        rayjoin_payload = rayjoin.v2_6_numba_compact_mask_plan_payload("pip")
        triangle_payload = triangle.v2_6_numba_compact_mask_plan_payload()

        for payload in (rayjoin_payload, triangle_payload):
            self.assertEqual(payload["selected_partner"], "numba")
            self.assertEqual(payload["operation"], "compact_mask_i64")
            self.assertTrue(payload["uses_v2_8_segmented_typed_stream_front_door"])
            self.assertFalse(payload["public_speedup_claim_authorized"])
            self.assertFalse(payload["rt_core_speedup_claim_authorized"])
            self.assertFalse(payload["true_zero_copy_claim_authorized"])

    def test_compact_mask_front_door_preserves_block_size_tuning_knob(self) -> None:
        fake_result = {
            "status": "completed",
            "outputs": {"values": (10, 12), "original_indices": (0, 2)},
            "stable_input_order": True,
            "host_prefix_sum_used": True,
            "phase_timing": {"phases_sec": {"partner_continuation": 0.001}},
        }

        with mock.patch(
            "rtdsl.numba_partner_continuation.run_numba_compact_mask_i64",
            return_value=fake_result,
        ) as compact:
            result = rt.execute_compact_mask_typed_stream_partner_columns(
                values=(10, 11, 12),
                mask=(True, False, True),
                partner="numba",
                block_size=512,
                stream_id="goal3151_compact_mask_schema",
                producer_primitive="schema_only_test_stream",
            )

        compact.assert_called_once()
        self.assertEqual(compact.call_args.kwargs["block_size"], 512)
        self.assertEqual(result["outputs"]["values"], (10, 12))
        self.assertEqual(result["partner_metadata"]["block_size"], 512)
        self.assertFalse(result["release_authorized"])

    def test_report_keeps_claim_boundary_blocked(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "release_authorized: False",
            "v2_8_release_authorized: False",
            "public_speedup_claim_authorized: False",
            "rt_core_speedup_claim_authorized: False",
            "true_zero_copy_claim_authorized: False",
            "paper_reproduction_claim_authorized: False",
            "automatic_partner_selection_allowed: False",
            "app_specific_engine_logic_allowed: False",
        ):
            self.assertIn(phrase, text)

    def test_external_review_handoff_names_required_review_questions(self) -> None:
        text = HANDOFF.read_text(encoding="utf-8")

        for phrase in (
            "Goal3151",
            "docs/reports/goal3151_v2_8_benchmark_front_door_adoption_audit_2026-06-03.md",
            "goal3152_claude_review_goal3151_v2_8_benchmark_front_door_adoption_2026-06-03.md",
            "goal3152_gemini_review_goal3151_v2_8_benchmark_front_door_adoption_2026-06-03.md",
            "no release, public speedup, RT-core speedup, true-zero-copy",
            "read-only review",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
