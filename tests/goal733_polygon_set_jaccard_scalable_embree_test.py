import unittest

from examples import rtdl_polygon_set_jaccard as app


class Goal733PolygonSetJaccardScalableEmbreeTest(unittest.TestCase):
    def test_copies_scale_area_totals_but_preserve_ratio(self) -> None:
        one = app.run_case("cpu_python_reference", copies=1)
        four = app.run_case("cpu_python_reference", copies=4)

        one_row = one["rows"][0]
        four_row = four["rows"][0]
        self.assertEqual(four["left_polygon_count"], 8)
        self.assertEqual(four["right_polygon_count"], 8)
        self.assertEqual(four_row["intersection_area"], int(one_row["intersection_area"]) * 4)
        self.assertEqual(four_row["left_area"], int(one_row["left_area"]) * 4)
        self.assertEqual(four_row["right_area"], int(one_row["right_area"]) * 4)
        self.assertEqual(four_row["union_area"], int(one_row["union_area"]) * 4)
        self.assertAlmostEqual(float(four_row["jaccard_similarity"]), float(one_row["jaccard_similarity"]))

    def test_embree_native_assisted_matches_cpu_reference_at_scale(self) -> None:
        expected = app.run_case("cpu_python_reference", copies=16)
        actual = app.run_case("embree", copies=16)

        self.assertEqual(actual["backend_mode"], "embree_native_assisted")
        self.assertEqual(actual["rows"], expected["rows"])
        self.assertEqual(actual["row_count"], expected["row_count"])
        self.assertGreater(actual["candidate_row_count"], 0)

    def test_rejects_invalid_copies(self) -> None:
        with self.assertRaisesRegex(ValueError, "copies must be >= 1"):
            app.make_authored_polygon_set_jaccard_case(copies=0)


if __name__ == "__main__":
    unittest.main()
