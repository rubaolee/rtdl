from __future__ import annotations

import inspect
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.action_api import (
    ActionCompilerError,
    ActionProducerKind,
    ActionTargetProfile,
    bind_action_producer,
    compile_bound_action_for_target,
)
from examples.current.research_benchmarks.contact_manifold import (
    rtdl3_effect_action_consumer as contact_consumer,
)


def _contact_bound():
    """Build the real non-paper contact-manifold Action without test-to-test imports."""

    return bind_action_producer(
        contact_consumer.compile_contact_action(),
        ActionProducerKind.PREPARED_AABB_OVERLAP_CANDIDATES_2D,
    )


def _target() -> ActionTargetProfile:
    return ActionTargetProfile(
        optix_available=True,
        cpu_reference_available=False,
        profile_source="runtime_capability_probe",
        device_memory_limit_bytes=8 << 30,
        production_selection_policy="compiler_owned_default",
    )


def _compile(*, statement: str | None = None, backend: str | None = None):
    return compile_bound_action_for_target(
        _contact_bound(),
        _target(),
        extents={},
        parameters={"row_capacity": 2},
        semantic_statement_stable_id=statement,
        backend_contract_id=backend,
    )


class Goal5731CommonActionProductionFrontdoorTest(unittest.TestCase):
    def test_canonical_statement_is_authority_and_default_is_materializer(self) -> None:
        planned = _compile(
            statement="aabb_overlap.filter_bounded_emit_2d.v1",
            backend="nvidia.optix_traversal.v1",
        )
        trace = planned.lowered.compiler_execution_trace["production_default"]
        self.assertTrue(trace["canonical_resolution_is_selection_authority"])
        self.assertFalse(trace["legacy_default_is_compatibility_materializer_only"])
        self.assertFalse(trace["legacy_default_is_selection_authority"])
        self.assertTrue(trace["canonical_provider_materializer_used"])
        self.assertFalse(trace["default_optimizer_selected_provider"])
        self.assertEqual(
            trace["canonical_resolution"]["provider_candidate_stable_id"],
            trace["plan"]["selected_candidate_stable_id"],
        )
        authority = trace["canonical_production_authority"]
        self.assertEqual(authority["status"], "BOUND")
        self.assertFalse(authority["candidate_executed"])
        self.assertTrue(authority["behavioral_receipt_still_required"])

    def test_statement_action_mismatch_fails_before_execution(self) -> None:
        with self.assertRaises(ActionCompilerError) as caught:
            _compile(
                statement="point_selection.spatial_bounded.v1",
                backend="nvidia.optix_traversal.v1",
            )
        self.assertEqual(
            caught.exception.issue.code,
            "canonical_physical_resolution_failed",
        )

    def test_incomplete_authority_fails_closed(self) -> None:
        with self.assertRaises(ActionCompilerError) as caught:
            _compile(statement="aabb_overlap.filter_bounded_emit_2d.v1")
        self.assertEqual(
            caught.exception.issue.code,
            "incomplete_canonical_semantic_authority",
        )

    def test_legacy_call_is_unchanged_but_not_canonical_authority(self) -> None:
        planned = _compile()
        trace = planned.lowered.compiler_execution_trace["production_default"]
        self.assertFalse(trace["canonical_resolution_is_selection_authority"])
        self.assertTrue(trace["legacy_default_is_selection_authority"])
        self.assertIsNone(trace["canonical_resolution"])

    def test_public_frontdoor_accepts_no_candidate_or_cost_input(self) -> None:
        parameters = set(inspect.signature(compile_bound_action_for_target).parameters)
        self.assertNotIn("candidate", parameters)
        self.assertNotIn("cost", parameters)
        self.assertNotIn("latency", parameters)
        self.assertIn("semantic_statement_stable_id", parameters)
        self.assertIn("backend_contract_id", parameters)


if __name__ == "__main__":
    unittest.main()
