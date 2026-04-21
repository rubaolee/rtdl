import unittest

from examples import rtdl_segment_polygon_anyhit_rows as app


class Goal726SegmentPolygonCompactSummaryTest(unittest.TestCase):
    def test_compact_modes_use_hitcount_primitive_and_match_rows(self) -> None:
        dataset = "derived/br_county_subset_segment_polygon_tiled_x16"
        rows_payload = app.run_case("cpu_python_reference", dataset, "rows")
        counts_payload = app.run_case("cpu_python_reference", dataset, "segment_counts")
        flags_payload = app.run_case("cpu_python_reference", dataset, "segment_flags")

        expected_counts: dict[int, int] = {}
        for row in rows_payload["rows"]:
            segment_id = int(row["segment_id"])
            expected_counts[segment_id] = expected_counts.get(segment_id, 0) + 1

        actual_counts = {
            int(row["segment_id"]): int(row["hit_count"])
            for row in counts_payload["segment_counts"]
        }
        actual_flags = {
            int(row["segment_id"]): int(row["any_hit"])
            for row in flags_payload["segment_flags"]
        }

        self.assertEqual(counts_payload["summary_source"], "segment_polygon_hitcount")
        self.assertEqual(flags_payload["summary_source"], "segment_polygon_hitcount")
        self.assertEqual(rows_payload["summary_source"], "segment_polygon_anyhit_rows")
        self.assertEqual(actual_counts, expected_counts)
        self.assertEqual(
            actual_flags,
            {segment_id: int(hit_count > 0) for segment_id, hit_count in expected_counts.items()},
        )
        self.assertLess(counts_payload["row_count"], rows_payload["row_count"])

    def test_embree_compact_mode_matches_cpu_reference(self) -> None:
        dataset = "derived/br_county_subset_segment_polygon_tiled_x16"
        expected = app.run_case("cpu_python_reference", dataset, "segment_counts")
        actual = app.run_case("embree", dataset, "segment_counts")

        self.assertEqual(actual["summary_source"], "segment_polygon_hitcount")
        self.assertEqual(actual["segment_counts"], expected["segment_counts"])


if __name__ == "__main__":
    unittest.main()
