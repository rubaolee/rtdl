from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal1274_v1_3_primitive_abi_lowering_contract_draft_2026-05-05.md"
)
CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal1274_three_ai_v1_3_primitive_contract_consensus_2026-05-05.md"
)


class Goal1274V13PrimitiveContractTest(unittest.TestCase):
    def test_contract_preserves_accepted_primitive_set(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        for phrase in (
            "`ANY_HIT`",
            "`COUNT_HITS`",
            "`REDUCE_FLOAT(MIN)`",
            "`REDUCE_FLOAT(MAX)`",
            "`REDUCE_FLOAT(SUM)`",
            "`REDUCE_INT(COUNT)`",
            "`REDUCE_INT(SUM)`",
            "`COLLECT_K_BOUNDED`",
            "experimental after scalar primitives are stable",
            "A single untyped\n`REDUCE` bucket is not precise enough",
            "Kahan-style accumulation",
            "matches exceed `k`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_contract_preserves_backend_scope_and_public_boundary(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        for phrase in (
            "active engineering scope is Embree plus OptiX",
            "Vulkan, HIPRT, and Apple RT stay frozen",
            "does not\nauthorize v1.4/v1.5 implementation",
            "public speedup wording still requires a separate exact-sub-path wording\n  packet",
            "final acceptance is a key goal and requires 3-AI consensus",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_contract_defines_abi_and_parity_fields(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        for phrase in (
            "`build_layout`",
            "`probe_layout`",
            "`result_layout`",
            "`group_key_layout`",
            "`precision_policy`",
            "`overflow_policy`",
            "`prepared_state`",
            "`phase_counters`",
            "`retained_scale_range`",
            "minimum NaN behavior",
            "floating reductions use declared absolute/relative tolerance",
            "unsupported backends fail with explicit `unsupported` or `blocked` status",
            "which state is immutable and reusable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_contract_covers_v1_2_target_lowerings(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        for phrase in (
            "`graph_analytics.visibility_edges`",
            "`database_analytics.sales_risk`",
            "`polygon_pair_overlap_area_rows`",
            "`polygon_set_jaccard`",
            "Goal1272: OptiX total and prepared repeat beat Embree",
            "Goal1272: OptiX warm-query median beats Embree",
            "Goal1272: OptiX candidate discovery beats Embree",
            "Goal1272: chunk `1024` is correctness-safe but OptiX remains slower",
            "preserve Goal1270 diagnostic split",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_contract_blocks_premature_v1_4_migration(self) -> None:
        text = CONTRACT.read_text(encoding="utf-8")

        self.assertIn("Until then, v1.4 native refactoring should not begin.", text)
        self.assertIn("No app-specific native continuation should be retired until", text)
        self.assertIn("no worse than 10% slower", text)

    def test_consensus_accepts_contract_and_preserves_boundaries(self) -> None:
        text = CONSENSUS.read_text(encoding="utf-8")

        for phrase in (
            "Status: `ACCEPT`",
            "Codex, Gemini, and Claude accept the v1.3 contract",
            "`REDUCE_FLOAT(SUM)`",
            "`REDUCE_INT(COUNT)`",
            "`COLLECT_K_BOUNDED`, experimental only",
            "Active v1.3/v1.4 engineering scope is Embree plus OptiX",
            "Vulkan, HIPRT, and Apple RT remain frozen",
            "does not by itself\nauthorize public RTX speedup wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
