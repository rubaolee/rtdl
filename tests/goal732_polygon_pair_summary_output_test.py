import unittest

from examples import rtdl_polygon_pair_overlap_area_rows as app


def _summary_from_rows(rows: tuple[dict[str, object], ...]) -> dict[str, int]:
    return {
        "overlap_pair_count": len(rows),
        "total_intersection_area": sum(int(row["intersection_area"]) for row in rows),
        "total_union_area": sum(int(row["union_area"]) for row in rows),
    }


class Goal732PolygonPairSummaryOutputTest(unittest.TestCase):
    def test_summary_matches_rows_for_cpu_reference(self) -> None:
        rows_payload = app.run_case("cpu_python_reference", copies=8, output_mode="rows")
        summary_payload = app.run_case("cpu_python_reference", copies=8, output_mode="summary")

        self.assertEqual(summary_payload["summary"], _summary_from_rows(rows_payload["rows"]))
        self.assertEqual(summary_payload["row_count"], rows_payload["row_count"])
        self.assertNotIn("rows", summary_payload)

    def test_embree_summary_matches_cpu_reference(self) -> None:
        expected = app.run_case("cpu_python_reference", copies=8, output_mode="summary")
        actual = app.run_case("embree", copies=8, output_mode="summary")

        self.assertEqual(actual["summary"], expected["summary"])
        self.assertEqual(actual["row_count"], expected["row_count"])
        self.assertNotIn("rows", actual)

    def test_default_rows_mode_keeps_rows(self) -> None:
        payload = app.run_case("cpu_python_reference")

        self.assertEqual(payload["output_mode"], "rows")
        self.assertEqual(payload["copies"], 1)
        self.assertIn("rows", payload)
        self.assertEqual(payload["summary"], _summary_from_rows(payload["rows"]))

    def test_rejects_invalid_options(self) -> None:
        with self.assertRaisesRegex(ValueError, "copies must be >= 1"):
            app.make_authored_polygon_pair_overlap_case(copies=0)
        with self.assertRaisesRegex(ValueError, "output_mode"):
            app.run_case("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
