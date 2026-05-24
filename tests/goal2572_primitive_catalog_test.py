from pathlib import Path
import unittest

from rtdsl.grouped_reduction import GROUPED_REDUCTION_OPERATIONS
from rtdsl.v1_5_migration_inventory import (
    V1_5_EXPERIMENTAL_GENERIC_PRIMITIVES,
    V1_5_STABLE_GENERIC_PRIMITIVES,
    V1_5_STABLE_SUMMARY_PRIMITIVES,
)


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs" / "rtdl_primitive_catalog.md"
REPORT = ROOT / "docs" / "reports" / "goal2572_primitive_catalog_and_promotion_rules_2026-05-23.md"
CLAUDE = ROOT / "docs" / "reports" / "goal2572_claude_primitive_catalog_review_2026-05-23.md"
GEMINI = ROOT / "docs" / "reports" / "goal2572_gemini_primitive_catalog_review_2026-05-23.md"
CONSENSUS = ROOT / "docs" / "reports" / "goal2572_3ai_consensus_primitive_catalog_2026-05-23.md"
BEHAVIOR_FIRST_CLAUDE = (
    ROOT
    / "docs"
    / "reports"
    / "goal2573_claude_behavior_first_primitive_taxonomy_review_2026-05-23.md"
)
BEHAVIOR_FIRST_GEMINI = (
    ROOT
    / "docs"
    / "reports"
    / "goal2573_gemini_behavior_first_primitive_taxonomy_review_2026-05-23.md"
)
BEHAVIOR_FIRST_CONSENSUS = (
    ROOT
    / "docs"
    / "reports"
    / "goal2573_3ai_consensus_behavior_first_primitive_taxonomy_2026-05-23.md"
)


class Goal2572PrimitiveCatalogTest(unittest.TestCase):
    def test_catalog_and_report_exist(self) -> None:
        for path in (
            CATALOG,
            REPORT,
            CLAUDE,
            GEMINI,
            CONSENSUS,
            BEHAVIOR_FIRST_CLAUDE,
            BEHAVIOR_FIRST_GEMINI,
            BEHAVIOR_FIRST_CONSENSUS,
        ):
            with self.subTest(path=path):
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertGreater(path.stat().st_size, 1000, f"truncated {path}")

    def test_catalog_lists_source_of_truth_primitives(self) -> None:
        text = CATALOG.read_text()
        for primitive in V1_5_STABLE_GENERIC_PRIMITIVES:
            with self.subTest(primitive=primitive):
                self.assertIn(primitive, text)
        for primitive in V1_5_STABLE_SUMMARY_PRIMITIVES:
            with self.subTest(primitive=primitive):
                self.assertIn(primitive, text)
        for primitive in V1_5_EXPERIMENTAL_GENERIC_PRIMITIVES:
            with self.subTest(primitive=primitive):
                self.assertIn(primitive, text)
        for operation in GROUPED_REDUCTION_OPERATIONS:
            with self.subTest(operation=operation):
                self.assertIn(operation, text)

    def test_catalog_is_behavior_first_not_layer_first(self) -> None:
        text = CATALOG.read_text()
        for phrase in [
            "Behavior-First Primitive Taxonomy",
            "The top-level organization is behavior",
            "Status metadata used below",
            "Hit And Traversal Predicates",
            "Spatial Neighborhood Predicates",
            "Exact Geometry Summaries",
            "Scalar Reductions",
            "Grouped And Keyed Reductions",
            "Columnar Compact Summaries",
            "Collection And Row Materialization",
            "Aggregate Frontier And Tree Traversal",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        for rejected_heading in [
            "Current Primitive Layers",
            "Layer 1:",
            "Layer 2:",
            "Layer 3:",
            "Layer 4:",
            "Layer 5:",
        ]:
            with self.subTest(rejected_heading=rejected_heading):
                self.assertNotIn(rejected_heading, text)

    def test_catalog_separates_primitives_from_app_code(self) -> None:
        text = CATALOG.read_text()
        for phrase in [
            "DBSCAN cluster expansion",
            "Robot pose/link sampling",
            "Barnes-Hut inverse-square force law",
            "App code",
            "App adapters",
            "partner code",
            "not native RTDL engine primitive",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_benchmark_injection_history_and_rejection_are_recorded(self) -> None:
        text = CATALOG.read_text()
        for phrase in [
            "Benchmark-App Primitive Injection History",
            "RT-DBSCAN",
            "Robot collision",
            "RayDB-style",
            "Barnes-Hut",
            "generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1",
            "hardcoded `source_weight * target_or_aggregate_weight / distance^2`",
            "Rejected candidate",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_promotion_and_user_selection_rules_are_present(self) -> None:
        text = CATALOG.read_text()
        for phrase in [
            "How Users Select Primitives",
            "Primitive Promotion Pipeline",
            "app code -> candidate primitive -> experimental primitive -> stable primitive",
            "Scheduling And Control Rules",
            "no silent truncation",
            "app-defined math must run in app/partner space",
            "native engine code must not contain app vocabulary",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_blocks_overclaims(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "does not authorize",
            "public release wording",
            "public speedup claims",
            "external ABI stability",
            "grouped-reduction operations as stable external primitives",
            "promoting `COLLECT_K_BOUNDED`",
            "treating app adapters as engine primitives",
            "claiming Barnes-Hut native aggregate-frontier support",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_report_records_behavior_first_correction(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "them first by stability/maturity is also wrong",
            "behavior the primary taxonomy",
            "Status is metadata, not the organizing axis",
            "hit/traversal predicate",
            "spatial neighborhood predicate",
            "grouped/keyed reduction",
            "aggregate-frontier candidate",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_external_reviews_and_consensus_are_recorded(self) -> None:
        claude = CLAUDE.read_text()
        gemini = GEMINI.read_text()
        consensus = CONSENSUS.read_text()
        self.assertIn("ACCEPT-WITH-BOUNDARY", claude)
        self.assertIn("VERDICT: ACCEPT", gemini)
        for phrase in [
            "Final verdict: `ACCEPT-WITH-BOUNDARY`",
            "primitive catalog",
            "app code -> candidate primitive -> experimental primitive -> stable primitive",
            "Accepted Claude Fix",
            "claiming Barnes-Hut native aggregate-frontier support",
            "not for public release or external ABI stability claims",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, consensus)

    def test_behavior_first_external_reviews_and_consensus_are_recorded(self) -> None:
        claude = BEHAVIOR_FIRST_CLAUDE.read_text()
        gemini = BEHAVIOR_FIRST_GEMINI.read_text()
        consensus = BEHAVIOR_FIRST_CONSENSUS.read_text()
        self.assertIn("Verdict: ACCEPT", claude)
        self.assertIn("Verdict: **ACCEPT**", gemini)
        for phrase in [
            "Final verdict: `ACCEPT`",
            "organized by behavior first",
            "Status is metadata",
            "supersedes any layer-first or maturity-first reading",
            "stable primitive | experimental primitive | internal substrate",
            "hit/traversal predicate",
            "App-specific semantics remain outside the engine",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, consensus)


if __name__ == "__main__":
    unittest.main()
