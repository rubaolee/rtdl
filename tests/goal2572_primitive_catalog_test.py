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


class Goal2572PrimitiveCatalogTest(unittest.TestCase):
    def test_catalog_and_report_exist(self) -> None:
        for path in (CATALOG, REPORT, CLAUDE, GEMINI, CONSENSUS):
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


if __name__ == "__main__":
    unittest.main()
