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
    / "build_xhd_goal5363_lb_heavy_offload_semantics_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5363_lb_heavy_offload_semantics_audit.json"
)


def _load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("goal5363_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5363LbHeavyOffloadSemanticsAuditTest(unittest.TestCase):
    def test_author_lb_semantics_are_extracted_from_source(self) -> None:
        payload = _load_module().build_artifact()
        self.assertEqual(
            "lb_heavy_offload_semantics_audit_ready__lb_option_still_unsupported",
            payload["status"],
        )
        self.assertTrue(payload["comparison"]["matched"])

        author = payload["author_lb_semantics"]
        self.assertTrue(author["all_required_source_evidence_found"])
        self.assertIsNotNone(
            author["lb_option_plumbing"]["flag_declared"]["line"],
            "author lb flag declaration should be pinned",
        )
        self.assertIsNotNone(
            author["lb_option_plumbing"]["main_assigns_config_lb"]["line"],
            "main.cpp should assign FLAGS_lb into config.lb",
        )

        zero_rule = author["semantic_rules"]["lb_zero_disables_offload_by_uint32_max_threshold"]
        self.assertEqual("identified", zero_rule["status"])
        self.assertIn("UINT32_MAX", zero_rule["interpretation"])
        for item in zero_rule["evidence"]:
            self.assertIsNotNone(item["line"])

        n_rule = author["semantic_rules"]["lb_n_offloads_cells_with_point_count_greater_than_n"]
        self.assertEqual("identified", n_rule["status"])
        self.assertIn("strictly greater than N", n_rule["interpretation"])
        for item in n_rule["evidence"]:
            self.assertIsNotNone(item["line"])

    def test_existing_rtdl_assets_are_shape_only_not_lb_support(self) -> None:
        payload = _load_module().build_artifact()
        assets = payload["existing_rtdl_assets"]["generic_assets_summary"]
        self.assertEqual("cell_point_count > max_inline_points", assets["nearest_state_frontier_threshold_rule"])
        self.assertTrue(assets["heavy_offload_worklist_exists"])
        self.assertTrue(assets["native_heavy_offload_telemetry_exists"])
        self.assertTrue(assets["author_offload_shape_mapping_exists"])
        self.assertFalse(assets["figure7_lb0_lbN_matrix_available"])
        self.assertFalse(assets["figure11_same_denominator_available"])

        decision = payload["semantic_mapping_decision"]
        self.assertFalse(decision["lb_option_supported_now"])
        self.assertEqual([], decision["accepted_explicit_author_lb_values"])
        self.assertTrue(decision["candidate_mapping_shape"]["shape_aligned"])
        self.assertEqual("cell_point_count > lb", decision["candidate_mapping_shape"]["author_lb_rule"])
        self.assertEqual(
            "cell_point_count > max_inline_points",
            decision["candidate_mapping_shape"]["rtdl_generic_threshold_rule"],
        )
        next_gate = decision["next_gate"]
        self.assertEqual("bounded_lb_processing_threshold_route_trace_gate", next_gate["name"])
        self.assertFalse(next_gate["candidate_rtdl_control"]["authorized_as_lb_mapping_now"])
        self.assertIn("lb=0", " ".join(next_gate["minimum_requirements"]))
        self.assertIn("lb=N", " ".join(next_gate["minimum_requirements"]))

    def test_saved_artifact_preserves_no_claim_boundary(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["comparison"]["matched"])
        self.assertIn("lb_heavy_offload", payload["exit_label"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)
        self.assertFalse(payload["semantic_mapping_decision"]["lb_option_supported_now"])


if __name__ == "__main__":
    unittest.main()
