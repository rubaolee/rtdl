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
    / "build_xhd_goal5366_lb_denominator_reconciliation.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5366_lb_denominator_reconciliation.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5366_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5366LbDenominatorReconciliationTest(unittest.TestCase):
    def test_reconciliation_identifies_formula_alignment_but_not_row_parity(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "lb_denominator_reconciliation_ready__row_count_parity_not_established",
            payload["status"],
        )
        qr = payload["quantitative_reconciliation"]
        self.assertTrue(qr["formula_denominator_aligned"])
        self.assertFalse(qr["row_count_parity"])
        self.assertFalse(qr["byte_parity_author_width"])
        self.assertFalse(qr["route_regime_aligned"])

        self.assertEqual(27133990, qr["author"]["offloading_size_rows"])
        self.assertEqual(217071920, qr["author"]["wl_heavy_peak_bytes"])
        self.assertEqual(24508120, qr["rtdl"]["heavy_offload_peak_rows"])
        self.assertEqual(196064960, qr["rtdl"]["author_width_candidate_bytes"])
        self.assertEqual(2625870, qr["deltas"]["row_delta_author_minus_rtdl"])
        self.assertEqual(21006960, qr["deltas"]["author_width_byte_delta_author_minus_rtdl"])

    def test_reconciliation_records_route_regime_mismatch_and_no_lb_support(self) -> None:
        payload = _load_module().build_artifact()
        interp = payload["denominator_interpretation"]
        self.assertIn("single-pass full-cover", interp["current_mismatch_reason"])
        self.assertIn("iterative radius/in_queue", interp["current_mismatch_reason"])
        self.assertEqual("behavior_level_only", interp["support_level"])

        q = payload["quantitative_reconciliation"]
        self.assertEqual(79.2156982421875, q["author"]["radius"])
        self.assertEqual(266.9466183641096, q["rtdl"]["radius"])
        self.assertTrue(q["rtdl"]["raw_attempted_equals_emitted_equals_offload_rows"])

        decision = payload["decision"]
        self.assertFalse(decision["explicit_lb_support_authorized_now"])
        self.assertFalse(decision["row_count_or_byte_parity_authorized_now"])
        self.assertIn("author-iteration-aligned", decision["next_gate"])

    def test_source_evidence_points_to_author_and_cell_mbr_frontier_code(self) -> None:
        payload = _load_module().build_artifact()
        self.assertTrue(payload["source_evidence"]["author_source_available"])
        author = payload["source_evidence"]["author"]
        self.assertIn("offloading_point_ids.Append", author["offload_append_point_id"]["text"])
        self.assertIn("OffloadingSize", author["json_offloading_size"]["text"])
        self.assertIn("reduce_by_key", author["load_balance_reduce_by_point"]["text"])

        rtdl = payload["source_evidence"]["rtdl"]
        self.assertIn("RtdlCellMbrFrontierRow", rtdl["row_sort"]["text"])
        self.assertIn("RtdlCellMbrFrontierRow", rtdl["row_unique"]["text"])
        self.assertIn("frontier_kind_code == 2", rtdl["offload_row_counter"]["text"])

    def test_saved_artifact_preserves_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("row_count_parity_not_established", payload["status"])
        self.assertIn("row_count_parity_not_established", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
