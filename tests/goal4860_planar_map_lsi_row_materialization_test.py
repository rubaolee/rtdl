import os
import unittest


class Goal4860PlanarMapLsiRowMaterializationTest(unittest.TestCase):
    def _assert_lsi_rows_match_count(self, base, query, expected_pairs):
        if not os.environ.get("RTDL_OPTIX_LIB"):
            self.skipTest("RTDL_OPTIX_LIB is required for the OptiX LSI row regression")

        from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix

        with prepare_planar_map_lsi_2d_optix(base) as prepared:
            count = prepared.count(query)
            rows = prepared.run_raw(query)
            try:
                materialized = rows.to_dict_rows()
            finally:
                rows.close()

        self.assertEqual(len(expected_pairs), count)
        self.assertEqual(len(expected_pairs), len(materialized))
        self.assertEqual(
            set(expected_pairs),
            {(row["left_id"], row["right_id"]) for row in materialized},
        )

    def test_minimal_real_witness_count_and_rows_share_lsi_contract(self):
        self._assert_lsi_rows_match_count(
            (
                {
                    "id": 14110870,
                    "x0": 151.2771671,
                    "y0": -33.8512399,
                    "x1": 151.2772023,
                    "y1": -33.8513923,
                },
                {
                    "id": 14387225,
                    "x0": 151.2771671,
                    "y0": -33.8512399,
                    "x1": 151.2772023,
                    "y1": -33.8513923,
                },
            ),
            (
                {
                    "id": 640,
                    "x0": 151.2776856,
                    "y0": -33.8511451,
                    "x1": 151.2772023,
                    "y1": -33.8513923,
                },
            ),
            {(640, 14110870), (640, 14387225)},
        )

    def test_endpoint_tolerance_witness_count_and_rows_share_lsi_contract(self):
        self._assert_lsi_rows_match_count(
            (
                {
                    "id": 34885,
                    "x0": 151.2948392,
                    "y0": -33.6428434,
                    "x1": 151.2950345,
                    "y1": -33.6426452,
                },
            ),
            (
                {
                    "id": 924275,
                    "x0": 151.2948522,
                    "y0": -33.6428304,
                    "x1": 151.2950345,
                    "y1": -33.6426452,
                },
            ),
            {(924275, 34885)},
        )

    def test_near_collinear_shared_endpoint_witness_materializes_row(self):
        self._assert_lsi_rows_match_count(
            (
                {
                    "id": 504748,
                    "x0": -123.481057,
                    "y0": 40.916257,
                    "x1": -123.481257,
                    "y1": 40.915857,
                },
            ),
            (
                {
                    "id": 234210,
                    "x0": -123.4810944,
                    "y0": 40.9161822,
                    "x1": -123.481257,
                    "y1": 40.915857,
                },
            ),
            {(234210, 504748)},
        )

    def test_endpoint_on_segment_interior_witness_materializes_row(self):
        self._assert_lsi_rows_match_count(
            (
                {
                    "id": 6445864,
                    "x0": -122.137585,
                    "y0": 43.459623,
                    "x1": -122.1375585,
                    "y1": 43.4596305,
                },
            ),
            (
                {
                    "id": 287389,
                    "x0": -122.13755,
                    "y0": 43.459633,
                    "x1": -122.137567,
                    "y1": 43.459628,
                },
            ),
            {(287389, 6445864)},
        )

    def test_near_collinear_overlap_witness_materializes_representative_row(self):
        self._assert_lsi_rows_match_count(
            (
                {
                    "id": 8014257,
                    "x0": -79.553631,
                    "y0": 38.559277,
                    "x1": -79.550511,
                    "y1": 38.557357,
                },
            ),
            (
                {
                    "id": 5202966,
                    "x0": -79.554671,
                    "y0": 38.559917,
                    "x1": -79.549471,
                    "y1": 38.556717,
                },
            ),
            {(5202966, 8014257)},
        )


if __name__ == "__main__":
    unittest.main()
