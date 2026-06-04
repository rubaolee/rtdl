from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3364_owner_face_cupy_review_gap_closure_2026-06-04.md"
REVIEW = ROOT / "docs" / "reviews" / "goal3363_claude_review_owner_face_cupy_continuation_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3364OwnerFaceCupyReviewGapClosureTest(unittest.TestCase):
    def test_contract_documents_cupy_filter_preconditions(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        filter_policy = contract["filter_policy"]

        self.assertEqual(
            filter_policy["device_cupy_filter_candidate_duplicates"],
            "fail_closed_by_default",
        )
        self.assertEqual(
            filter_policy["device_cupy_filter_face_ids"],
            "non_negative_matches_only",
        )
        self.assertEqual(
            filter_policy["device_cupy_filter_owner_multiplicity"],
            "single_owner_face_per_point_only",
        )

    def test_cupy_filter_rejects_duplicate_candidate_pairs(self):
        cp = _cupy_or_skip(self)

        with self.assertRaisesRegex(ValueError, "candidate point/shape pairs must be unique"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
                candidate_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                candidate_shape_ids=cp.asarray((100, 100), dtype=cp.int64),
                topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
                topology_right_face_ids=cp.asarray((11,), dtype=cp.int64),
                owner_point_ids=cp.asarray((1,), dtype=cp.int64),
                owner_face_ids=cp.asarray((10,), dtype=cp.int64),
            )

    def test_cupy_filter_rejects_multi_owner_opt_out(self):
        cp = _cupy_or_skip(self)

        with self.assertRaisesRegex(ValueError, "multiple owner faces per point"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
                candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
                candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
                topology_right_face_ids=cp.asarray((11,), dtype=cp.int64),
                owner_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                owner_face_ids=cp.asarray((10, 11), dtype=cp.int64),
                require_unique_owner_point=False,
            )

    def test_cupy_filter_excludes_negative_face_ids_like_reference(self):
        cp = _cupy_or_skip(self)
        expected = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1,),
            candidate_shape_ids=(100,),
            topology_shape_ids=(100,),
            topology_left_face_ids=(-1,),
            topology_right_face_ids=(20,),
            owner_point_ids=(1,),
            owner_face_ids=(-1,),
        )
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
            candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((-1,), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((20,), dtype=cp.int64),
            owner_point_ids=cp.asarray((1,), dtype=cp.int64),
            owner_face_ids=cp.asarray((-1,), dtype=cp.int64),
        )

        self.assertEqual(expected["point_id"], ())
        self.assertEqual(_host_tuple(actual["point_id"]), ())
        self.assertEqual(_host_tuple(actual["shape_id"]), ())
        self.assertEqual(_host_tuple(actual["membership"]), ())
        self.assertEqual(_host_tuple(actual["owner_face_id"]), ())

    def test_report_records_claude_closure(self):
        text = REPORT.read_text(encoding="utf-8")
        review = REVIEW.read_text(encoding="utf-8")

        self.assertIn("Goal3363 Claude review", text)
        self.assertIn("duplicate candidate", text)
        self.assertIn("negative face", text)
        self.assertIn("single-owner-face-per-point", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 20 tests in 0.743s", text)
        self.assertIn("Ran 80 tests in 0.766s", text)
        self.assertIn("accept-with-boundary", review)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
