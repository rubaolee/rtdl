import unittest
from pathlib import Path

from src.rtdsl.python_rtdl_app_purity import (
    EXPERIMENTAL_PRIMITIVE_BLOCKED,
    LEGACY_ENGINE_CUSTOMIZED,
    PURE_APP_READY,
    PYTHON_RTDL_FASTEST_COLLECT_K_ENV,
    native_symbol_purity_audit,
    python_rtdl_app_purity_matrix,
    validate_python_rtdl_product_checkpoint,
)


ROOT = Path(__file__).resolve().parents[1]
PERF_REPORT = ROOT / "docs" / "reports" / "goal1658_v1_6_x_optix_collect_k_perf_checkpoint_2026-05-10.md"
PROJECT_CHECKPOINT = ROOT / "docs" / "reports" / "goal1658_python_rtdl_v2_5_product_checkpoint_2026-05-10.md"


class Goal1658PythonRtdlProductCheckpointTest(unittest.TestCase):
    def test_perf_report_freezes_fastest_solution_until_v2_5(self) -> None:
        text = PERF_REPORT.read_text(encoding="utf-8")
        for phrase in [
            "`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE=1`",
            "`row_width2_bounded_multi_tile_sort_merge`",
            "`candidate_count=262144`",
            "`total_ms=0.637297`",
            "No more collect-k optimization studies before v2.5",
            "does not authorize public speedup wording",
            "does not promote `COLLECT_K_BOUNDED` to stable",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_project_checkpoint_names_python_rtdl_purity_rule(self) -> None:
        text = PROJECT_CHECKPOINT.read_text(encoding="utf-8")
        for phrase in [
            "app logic must be implemented in Python",
            "engines must expose generic RTDL primitives",
            "app-shaped native continuations are legacy/proof machinery",
            "not yet fully product-ready",
            "No new OptiX collect-k optimization candidates before v2.5",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_native_audit_no_longer_detects_legacy_app_shaped_exports(self) -> None:
        audit = native_symbol_purity_audit(repo_root=ROOT)
        self.assertGreaterEqual(len(audit["native_symbols"]), 100)
        self.assertEqual(len(audit["legacy_engine_customized_symbols"]), 0)
        symbols = {row.symbol for row in audit["legacy_engine_customized_symbols"]}
        for symbol in [
            "rtdl_optix_run_shape_pair_relation_flags",
            "rtdl_optix_run_segment_pair_intersection",
            "rtdl_embree_run_edge_neighbor_intersection_packet",
        ]:
            with self.subTest(symbol=symbol):
                self.assertNotIn(symbol, symbols)
        self.assertFalse(audit["pure_native_app_contract_ready"])

    def test_app_matrix_separates_pure_target_from_blockers(self) -> None:
        matrix = python_rtdl_app_purity_matrix()
        for app in [
            "event_hotspot_screening",
            "dbscan_clustering",
            "polygon_set_jaccard",
            "database_analytics",
        ]:
            with self.subTest(app=app):
                self.assertIn(app, matrix)
        self.assertEqual(matrix["event_hotspot_screening"]["status"], PURE_APP_READY)
        self.assertEqual(matrix["dbscan_clustering"]["status"], PURE_APP_READY)
        self.assertEqual(matrix["polygon_set_jaccard"]["status"], EXPERIMENTAL_PRIMITIVE_BLOCKED)
        self.assertEqual(matrix["database_analytics"]["status"], LEGACY_ENGINE_CUSTOMIZED)

    def test_product_checkpoint_is_fail_closed_until_migration_finishes(self) -> None:
        checkpoint = validate_python_rtdl_product_checkpoint(repo_root=ROOT)
        self.assertFalse(checkpoint["product_ready"])
        self.assertEqual(checkpoint["optimization_freeze_until"], "v2.5")
        self.assertEqual(checkpoint["fastest_collect_k_env"], PYTHON_RTDL_FASTEST_COLLECT_K_ENV)
        self.assertIn("database_analytics", checkpoint["app_blockers"])
        self.assertIn("polygon_set_jaccard", checkpoint["app_blockers"])


if __name__ == "__main__":
    unittest.main()
