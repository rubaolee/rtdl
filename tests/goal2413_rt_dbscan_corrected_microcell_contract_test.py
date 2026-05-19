from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "docs" / "reviews" / "goal2412_claude_review_goal2411_microcell_counter_review_2026-05-19.md"
CONTRACT = ROOT / "docs" / "reports" / "goal2413_rt_dbscan_corrected_microcell_next_fight_contract_2026-05-19.md"


class Goal2413RtDbscanCorrectedMicrocellContractTest(unittest.TestCase):
    def test_claude_accepts_the_microcell_correction(self) -> None:
        review = CLAUDE.read_text(encoding="utf-8")

        self.assertIn("Verdict: **accept**", review)
        self.assertIn("my Goal2409 review missed that gap", review)
        self.assertIn("microcell_size = radius / sqrt(3)", review)
        self.assertIn("radius_graph_components_3d_cupy_microcell_graph_partner_columns", review)

    def test_contract_rejects_radius_cell_graph_and_names_microcell_target(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")

        self.assertIn("radius-cell component graph must not be implemented", contract)
        self.assertIn("generic fixed-radius microcell component continuation", contract)
        self.assertIn("optix_rt_core_flags_cupy_microcell_graph_components_3d", contract)
        self.assertIn("clique_safe_microcell", contract)

    def test_contract_preserves_schema_evidence_and_abort_policy(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")

        self.assertIn("point_ids, component_labels, is_core, neighbor_counts", contract)
        self.assertIn("signatures_match == true", contract)
        self.assertIn("same-cell disconnected cases merge incorrectly", contract)
        self.assertIn("app-agnostic", contract)


if __name__ == "__main__":
    unittest.main()
