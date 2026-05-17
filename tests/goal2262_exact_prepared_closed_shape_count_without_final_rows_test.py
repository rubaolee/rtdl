from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal2262_exact_prepared_closed_shape_count_without_final_rows_2026-05-17.md"


class Goal2262ExactPreparedClosedShapeCountWithoutFinalRowsTest(unittest.TestCase):
    def test_count_path_no_longer_calls_row_return_path(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static void count_prepared_point_closed_shape_membership_2d_optix")
        end = text.index("static void run_shape_pair_relation_flags_with_prepared_right_optix", start)
        count_body = text[start:end]

        self.assertNotIn("run_prepared_point_closed_shape_membership_2d_optix(", count_body)
        self.assertNotIn("RtdlPointClosedShapeMembershipRow* rows", count_body)
        self.assertIn("count_exact_hits", count_body)
        self.assertIn("*count_out = exact_count", count_body)

    def test_count_path_preserves_exact_refinement(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static void count_prepared_point_closed_shape_membership_2d_optix")
        end = text.index("static void run_shape_pair_relation_flags_with_prepared_right_optix", start)
        count_body = text[start:end]

        self.assertIn("prepared->right_geos->covers", count_body)
        self.assertIn("exact_point_in_polygon", count_body)
        self.assertIn("download(chunk_rows.data()", count_body)

    def test_report_keeps_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Without Final Rows", text)
        self.assertIn("not a pure", text)
        self.assertIn("pod timing recorded by Goal2263", text)
        self.assertIn("the measured exact-count claim lives in the Goal2263", text)


if __name__ == "__main__":
    unittest.main()
