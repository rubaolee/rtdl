from __future__ import annotations

import unittest
from unittest import mock

import rtdsl as rt
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


class Goal948PolygonNativeContinuationTest(unittest.TestCase):
    @staticmethod
    def _fake_optix_rows(kernel, **_inputs):
        if kernel.__name__ == "polygon_edge_intersections_embree_kernel":
            return (
                {"left_id": 1, "right_id": 10, "x": 1.0, "y": 1.0},
                {"left_id": 2, "right_id": 11, "x": 5.0, "y": 1.0},
            )
        if kernel.__name__ == "polygon_point_in_polygon_positive_embree_kernel":
            return ()
        raise AssertionError(f"unexpected kernel {kernel.__name__}")

    def test_native_pair_refinement_matches_python_candidate_refinement(self) -> None:
        case = pair_app.make_authored_polygon_pair_overlap_case(copies=2)
        candidate_pairs = {(1, 10), (2, 11), (101, 110), (102, 111), (1, 12)}
        native_rows = rt.refine_polygon_pair_overlap_area_rows_for_pairs(
            case["left"],
            case["right"],
            candidate_pairs,
        )
        python_rows = pair_app._exact_overlap_rows_for_candidates(
            case["left"],
            case["right"],
            candidate_pairs,
        )
        self.assertEqual(native_rows, python_rows)

    def test_native_jaccard_refinement_matches_python_candidate_refinement(self) -> None:
        case = jaccard_app.make_authored_polygon_set_jaccard_case(copies=2)
        candidate_pairs = {(1, 10), (2, 11), (101, 110), (102, 111)}
        native_rows = rt.refine_polygon_set_jaccard_for_pairs(
            case["left"],
            case["right"],
            candidate_pairs,
        )
        python_rows = jaccard_app._exact_jaccard_rows_for_candidates(
            case["left"],
            case["right"],
            candidate_pairs,
        )
        self.assertEqual(native_rows, python_rows)

    def test_pair_app_marks_native_continuation_after_optix_candidate_discovery(self) -> None:
        with mock.patch.object(rt, "run_optix", side_effect=self._fake_optix_rows):
            payload = pair_app.run_case("optix")
        self.assertTrue(payload["rt_core_candidate_discovery_active"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp")
        self.assertIn("native C++ exact grid-cell area continuation", payload["boundary"])

    def test_jaccard_app_marks_native_continuation_after_optix_candidate_discovery(self) -> None:
        with mock.patch.object(rt, "run_optix", side_effect=self._fake_optix_rows):
            payload = jaccard_app.run_case("optix")
        self.assertTrue(payload["rt_core_candidate_discovery_active"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "oracle_cpp")
        self.assertIn("native C++ exact grid-cell set-area continuation", payload["boundary"])


if __name__ == "__main__":
    unittest.main()
