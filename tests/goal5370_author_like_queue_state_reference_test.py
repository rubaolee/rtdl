from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5370_author_like_queue_state_reference.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5370_author_like_queue_state_reference.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5370_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5370AuthorLikeQueueStateReferenceTest(unittest.TestCase):
    def test_queue_state_reference_matches_author_rows_and_exposes_state_vectors(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual("bounded_author_like_queue_state_reference_ready", payload["status"])
        self.assertEqual(
            "bounded_queue_state_reference_matches_author_rows__dragon_lb_still_unimplemented",
            payload["exit_label"],
        )
        self.assertTrue(payload["comparison"]["matched"])
        self.assertEqual(0, payload["comparison"]["mismatch_count"])

        states = payload["rtdl_queue_state_reference"]["iterations"]
        self.assertGreaterEqual(len(states), 1)
        first = states[0]
        row = first["queue_row"]
        self.assertEqual(row["NumInputPoints"], len(first["active_source_ids"]))
        self.assertEqual(row["NumInputPoints"], len(first["active_in_queue_indices"]))
        self.assertEqual(row["NumInputPoints"], len(first["nearest_distances"]))
        self.assertEqual(row["NumInputPoints"], len(first["current_best_sq"]))
        self.assertEqual(row["NumInputPoints"], len(first["confirmed_source_ids"]) + len(first["unresolved_source_ids"]))

        for state in states:
            active_ids = state["active_source_ids"]
            self.assertEqual(list(range(len(active_ids))), state["active_in_queue_indices"])
            self.assertEqual(
                state["queue_row"]["NumOutputPoints"],
                len(state["unresolved_source_ids"]),
            )

    def test_artifact_records_generic_pipeline_and_blocks_lb_claims(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        reference = data["rtdl_queue_state_reference"]
        self.assertTrue(reference["uses_generic_nearest_pipeline"])
        self.assertIn("active_source_ids", reference["state_fields"])
        self.assertIn("current_best_sq", reference["state_fields"])
        self.assertIn("unresolved_source_ids", reference["state_fields"])

        claims = data["claim_boundary"]
        self.assertTrue(claims["queue_state_reference_claimed"])
        for key in (
            "explicit_lb_support_claimed",
            "dragon_asian_lb_denominator_claimed",
            "row_count_parity_claimed",
            "figure7_reproduction_claimed",
            "figure11_reproduction_claimed",
            "author_rt_core_algorithm_parity_claimed",
            "performance_claimed",
            "full_xhd_paper_reproduction_claimed",
        ):
            self.assertFalse(claims[key], key)


if __name__ == "__main__":
    unittest.main()
