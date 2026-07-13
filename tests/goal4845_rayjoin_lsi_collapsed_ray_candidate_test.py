import os
import unittest


class Goal4845RayjoinLsiCollapsedRayCandidateTest(unittest.TestCase):
    def test_collapsed_float_ray_still_reaches_exact_lsi_predicate(self):
        if not os.environ.get("RTDL_OPTIX_LIB"):
            self.skipTest("RTDL_OPTIX_LIB is required for the OptiX synthetic regression")

        from rtdsl import Segment
        from rtdsl.optix_runtime import (
            prepare_segment_pair_intersection_optix,
            prepare_segment_pair_left_set_optix,
        )
        from rtdsl.rayjoin_overlay import _rayjoin_lsi_predicate_env

        min_x, max_x = -179.148909, 179.778465
        min_y, max_y = -14.548692, 71.390482
        county = Segment(
            id=8480675,
            x0=-78.550846,
            y0=39.124448,
            x1=-78.552278,
            y1=39.125105,
        )
        zipcode = Segment(
            id=5748177,
            x0=-78.5510145,
            y0=39.1245252,
            x1=-78.5510215,
            y1=39.1245286,
        )
        scale_dummies = [
            Segment(id=900000001, x0=min_x, y0=min_y, x1=min_x, y1=min_y),
            Segment(id=900000002, x0=max_x, y0=max_y, x1=max_x, y1=max_y),
        ]

        with _rayjoin_lsi_predicate_env("optix"):
            prepared = prepare_segment_pair_intersection_optix([county, *scale_dummies])
            prepared_left = prepare_segment_pair_left_set_optix([zipcode, *scale_dummies])
            try:
                direct = prepared.count_prepared_left_direct_intersection(prepared_left)
                grouped = prepared.count_prepared_left_grouped_range_direct_intersection(prepared_left)
            finally:
                prepared_left.close()
                prepared.close()

        self.assertEqual(direct["count"], 1)
        self.assertEqual(grouped["count"], 1)


if __name__ == "__main__":
    unittest.main()
