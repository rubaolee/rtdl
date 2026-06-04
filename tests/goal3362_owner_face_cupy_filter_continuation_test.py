from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3362_owner_face_cupy_filter_continuation_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3362OwnerFaceCupyFilterContinuationTest(unittest.TestCase):
    def test_contract_lists_cupy_filter_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "filter_closed_shape_membership_candidate_columns_by_owner_face_cupy",
            contract["optional_columnar_pipeline_helpers"],
        )

    def test_cupy_filter_matches_python_columnar_reference(self):
        cp = _cupy_or_skip(self)
        expected = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1, 1, 2),
            candidate_shape_ids=(100, 101, 102),
            topology_shape_ids=(100, 101, 102),
            topology_left_face_ids=(10, 20, 30),
            topology_right_face_ids=(11, 21, 31),
            owner_point_ids=(1, 2),
            owner_face_ids=(20, 30),
        )
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
            candidate_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100, 101, 102), dtype=cp.int64),
            topology_shape_ids=cp.asarray((100, 101, 102), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((11, 21, 31), dtype=cp.int64),
            owner_point_ids=cp.asarray((1, 2), dtype=cp.int64),
            owner_face_ids=cp.asarray((20, 30), dtype=cp.int64),
        )

        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["shape_id"]), expected["shape_id"])
        self.assertEqual(_host_tuple(actual["membership"]), expected["membership"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])

    def test_cupy_filter_honors_missing_topology_and_face_presence(self):
        cp = _cupy_or_skip(self)
        missing_topology = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
            candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_shape_ids=cp.asarray((), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((), dtype=cp.int64),
            owner_point_ids=cp.asarray((1,), dtype=cp.int64),
            owner_face_ids=cp.asarray((10,), dtype=cp.int64),
        )
        gated_left = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
            candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((20,), dtype=cp.int64),
            topology_has_left_faces=cp.asarray((0,), dtype=cp.int8),
            topology_has_right_faces=cp.asarray((1,), dtype=cp.int8),
            owner_point_ids=cp.asarray((1,), dtype=cp.int64),
            owner_face_ids=cp.asarray((10,), dtype=cp.int64),
        )

        self.assertEqual(_host_tuple(missing_topology["point_id"]), ())
        self.assertEqual(_host_tuple(gated_left["point_id"]), ())

    def test_cupy_filter_fails_closed_on_missing_or_duplicate_owner(self):
        cp = _cupy_or_skip(self)
        with self.assertRaisesRegex(KeyError, "missing owner face"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
                candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
                candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
                topology_right_face_ids=cp.asarray((11,), dtype=cp.int64),
                owner_point_ids=cp.asarray((), dtype=cp.int64),
                owner_face_ids=cp.asarray((), dtype=cp.int64),
            )
        with self.assertRaisesRegex(ValueError, "owner point ids must be unique"):
            rt.filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
                candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
                candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
                topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
                topology_right_face_ids=cp.asarray((11,), dtype=cp.int64),
                owner_point_ids=cp.asarray((1, 1), dtype=cp.int64),
                owner_face_ids=cp.asarray((10, 11), dtype=cp.int64),
            )

    def test_report_keeps_cupy_continuation_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("CuPy device-column continuation", text)
        self.assertIn("not native RT traversal", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("pod evidence required", text)
        self.assertIn("Ran 15 tests in 8.593s", text)


if __name__ == "__main__":
    unittest.main()
