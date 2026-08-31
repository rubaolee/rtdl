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
    / "build_xhd_goal5367_lb_author_radius_probe.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5367_lb_author_radius_probe.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5367_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5367LbAuthorRadiusProbeTest(unittest.TestCase):
    def test_author_radius_probe_preserves_value_but_not_row_parity(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "author_radius_lb_probe_ready__radius_alignment_not_sufficient_for_row_parity",
            payload["status"],
        )
        comparison = payload["comparison"]
        self.assertTrue(comparison["explicit_radius_matches_author_value"])
        self.assertTrue(comparison["radius_aligned"])
        self.assertFalse(comparison["row_count_parity"])
        self.assertFalse(comparison["author_radius_closes_denominator_gap"])
        self.assertEqual(27133990, comparison["author_offloading_size_rows"])
        self.assertEqual(21006960, comparison["author_radius_row_count"])
        self.assertEqual(6127030, comparison["row_delta_author_minus_author_radius_rtdl"])

    def test_author_radius_reduces_rows_relative_to_full_cover_probe(self) -> None:
        payload = _load_module().build_artifact()
        comparison = payload["comparison"]
        self.assertTrue(comparison["author_radius_reduces_rows_vs_full_cover"])
        self.assertEqual(24508120, comparison["full_cover_row_count"])
        self.assertEqual(21006960, comparison["author_radius_row_count"])
        self.assertEqual(3501160, comparison["row_delta_full_cover_minus_author_radius"])

        routes = payload["rtdl_routes"]
        self.assertEqual(266.9466183641096, routes["full_cover_radius_lb256_from_goal5365"]["radius"])
        self.assertEqual(79.2156982421875, routes["author_iteration_radius_lb256_probe"]["radius"])
        self.assertGreater(
            routes["full_cover_radius_lb256_from_goal5365"]["rtdl_route_sec"],
            routes["author_iteration_radius_lb256_probe"]["rtdl_route_sec"],
        )

    def test_claim_boundary_and_next_gate_are_strict(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("not_lb_denominator_parity", payload["exit_label"])
        self.assertFalse(payload["decision"]["explicit_lb_support_authorized_now"])
        self.assertFalse(payload["decision"]["row_count_parity_authorized_now"])
        self.assertIn("in_queue_cmin2", payload["decision"]["next_gate"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
