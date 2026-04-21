import unittest

from examples import rtdl_road_hazard_screening as app


class Goal729RoadHazardCompactOutputTest(unittest.TestCase):
    def test_compact_modes_omit_rows_but_preserve_priority_segments(self) -> None:
        rows_payload = app.run_case("cpu_python_reference", copies=8, output_mode="rows")
        priority_payload = app.run_case("cpu_python_reference", copies=8, output_mode="priority_segments")
        summary_payload = app.run_case("cpu_python_reference", copies=8, output_mode="summary")

        self.assertIn("rows", rows_payload)
        self.assertNotIn("rows", priority_payload)
        self.assertNotIn("rows", summary_payload)
        self.assertEqual(priority_payload["priority_segments"], rows_payload["priority_segments"])
        self.assertEqual(summary_payload["priority_segments"], rows_payload["priority_segments"])
        self.assertEqual(priority_payload["priority_segment_count"], len(rows_payload["priority_segments"]))
        self.assertEqual(summary_payload["priority_segment_count"], len(rows_payload["priority_segments"]))
        self.assertEqual(priority_payload["row_count"], rows_payload["row_count"])
        self.assertEqual(summary_payload["row_count"], rows_payload["row_count"])

    def test_embree_compact_output_matches_cpu_reference(self) -> None:
        expected = app.run_case("cpu_python_reference", copies=8, output_mode="priority_segments")
        actual = app.run_case("embree", copies=8, output_mode="priority_segments")

        self.assertEqual(actual["priority_segments"], expected["priority_segments"])
        self.assertEqual(actual["priority_segment_count"], expected["priority_segment_count"])
        self.assertEqual(actual["row_count"], expected["row_count"])

    def test_rejects_invalid_copies_and_output_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "copies must be positive"):
            app.make_demo_case(copies=0)
        with self.assertRaisesRegex(ValueError, "output_mode"):
            app.run_case("cpu_python_reference", output_mode="bad")


if __name__ == "__main__":
    unittest.main()
