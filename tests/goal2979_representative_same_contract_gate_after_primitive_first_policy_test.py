from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2979_representative_same_contract_gate_after_primitive_first_policy_2026-06-01.md"
)
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2979_same_contract_representative_gate_pod"
EXPECTED_COMMIT = "6fd7be7c9ab20b2128634cfffb6e673caf2c8824"


class Goal2979RepresentativeSameContractGateTest(unittest.TestCase):
    def test_raydb_current_gate_remains_primitive_first(self) -> None:
        gate = json.loads((ARTIFACT_DIR / "raydb_current.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", gate["status"])
        self.assertEqual(EXPECTED_COMMIT, gate["git_head"])
        self.assertEqual([], gate["errors"])
        self.assertTrue(gate["all_correct"])
        self.assertEqual(
            "paper_rt_optix_v2_5_primitive_first",
            gate["decision"]["raydb_scalar_grouped_fast_path"],
        )
        self.assertFalse(gate["decision"]["auto_triton_promotion_authorized"])
        for row in gate["comparisons"]:
            with self.subTest(row_count=row["row_count"], mode=row["mode"]):
                self.assertTrue(row["pass"])
                self.assertGreaterEqual(
                    float(row["prepared_hit_stream_triton_slowdown_vs_primitive_first"]),
                    float(row["required_min_slowdown"]),
                )

    def test_rt_dbscan_grouped_stream_uses_rt_and_avoids_large_streams(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "rt_dbscan.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertTrue(payload["signatures_match"])
        self.assertTrue(payload["grouped_stream_rt_core_accelerated"])
        self.assertTrue(payload["grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream"])
        self.assertGreaterEqual(float(payload["min_grouped_stream_speedup_vs_prepared_cupy_grid"]), 3.8)
        self.assertGreaterEqual(float(payload["max_grouped_stream_speedup_vs_prepared_cupy_grid"]), 4.9)
        for row in payload["rows"]:
            self.assertTrue(row["grouped_stream_signature_match"])
            self.assertTrue(row["grouped_stream_rt_core_accelerated"])
            self.assertFalse(row["grouped_stream_materializes_neighbor_rows"])
            self.assertFalse(row["grouped_stream_materializes_directed_adjacency_stream"])

    def test_grouped_vector_partner_choice_is_measured_not_auto_triton(self) -> None:
        payload = json.loads((ARTIFACT_DIR / "vector_partner.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", payload["status"])
        self.assertEqual(EXPECTED_COMMIT, payload["source_commit"])
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("cupy_add_at", payload["winner"]["partner"])
        self.assertTrue(all(payload["matches"].values()))
        self.assertGreater(float(payload["ratios"]["triton_over_torch"]), 6.0)
        self.assertLess(float(payload["ratios"]["cupy_offsets_over_torch"]), 1.0)
        self.assertFalse(payload["claim_boundary"]["triton_preview_auto_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["v2_5_release_authorized"])
        self.assertFalse(payload["claim_boundary"]["native_engine_customization"])

    def test_report_and_readiness_index_the_gate_without_release_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)

        for phrase in (
            "Goal2979",
            "Representative Same-Contract Gate",
            "`43.850x`",
            "`4.930x`",
            "same-contract measurement",
            "does not authorize",
        ):
            self.assertIn(phrase, text)
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2978_primitive_first_v2_5_closeout_policy_2026-06-01.md"
            ]
        )
        self.assertTrue(
            packet["required_report_presence"][
                "docs/reports/goal2979_representative_same_contract_gate_after_primitive_first_policy_2026-06-01.md"
            ]
        )
        self.assertIn("keep_goal2979_representative_same_contract_gate_green", packet["allowed_next_actions"])
        self.assertFalse(packet["claim_authorization"]["v2_5_release_authorized"])
        self.assertEqual("accept", rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)["status"])


if __name__ == "__main__":
    unittest.main()
