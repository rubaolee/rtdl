from __future__ import annotations

from pathlib import Path
import unittest

from examples import rtdl_graph_analytics_app as graph_app
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app
from examples import rtdl_sales_risk_screening as sales_app


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1281_v1_4_wrapper_consolidation_status_2026-05-05.md"


class Goal1281V14WrapperConsolidationStatusTest(unittest.TestCase):
    def test_report_covers_all_goal1274_target_rows_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "`graph_analytics.visibility_edges`",
            "`database_analytics.sales_risk`",
            "`polygon_pair_overlap_area_rows`",
            "`polygon_set_jaccard`",
            "`optix_still_slower_with_reason`",
            "Vulkan/HIPRT/Apple RT proof paths are not expanded",
            "schema normalization",
            "before requesting another pod",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_current_apps_emit_primitive_contracts_for_target_rows(self) -> None:
        graph = graph_app.run_app("cpu_python_reference", "visibility_edges", output_mode="summary")
        sales = sales_app.run_case("cpu_python_reference", output_mode="summary")
        pair = pair_app.run_case("cpu_python_reference", output_mode="summary")
        jaccard = jaccard_app.run_case("cpu_python_reference", output_mode="summary")

        self.assertEqual(
            graph["sections"]["visibility_edges"]["primitive_contract"]["app_row"],
            "graph_analytics.visibility_edges",
        )
        self.assertEqual(sales["primitive_contract"]["app_row"], "database_analytics.sales_risk")
        self.assertEqual(pair["primitive_contract"]["app_row"], "polygon_pair_overlap_area_rows")
        self.assertEqual(jaccard["primitive_contract"]["app_row"], "polygon_set_jaccard")
        self.assertFalse(jaccard["primitive_contract"]["public_wording_allowed"])


if __name__ == "__main__":
    unittest.main()
