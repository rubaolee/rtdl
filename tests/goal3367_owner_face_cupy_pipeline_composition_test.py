from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3367_owner_face_cupy_pipeline_composition_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3367OwnerFaceCupyPipelineCompositionTest(unittest.TestCase):
    def test_contract_lists_composed_cupy_pipeline(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "run_closed_shape_owner_face_priority_membership_pipeline_cupy",
            contract["optional_columnar_pipeline_helpers"],
        )

    def test_cupy_pipeline_matches_python_columnar_selection_and_filter(self):
        cp = _cupy_or_skip(self)
        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=(1, 1, 2),
            face_ids=(10, 20, 30),
            rank_columns={"rank0": (5, 1, 0)},
            rank_fields=("rank0",),
        )
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=(1, 1, 2),
            incident_face_ids=(10, 20, 30),
            incident_face_counts=(2, 2, 1),
            priority_point_ids=priority_columns["point_id"],
            priority_face_ids=priority_columns["face_id"],
            priorities=priority_columns["priority"],
        )
        expected = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=(1, 1, 2),
            candidate_shape_ids=(100, 101, 102),
            topology_shape_ids=(100, 101, 102),
            topology_left_face_ids=(10, 20, 30),
            topology_right_face_ids=(11, 21, 31),
            owner_point_ids=selected_columns["point_id"],
            owner_face_ids=selected_columns["owner_face_id"],
        )
        actual = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2, 1), dtype=cp.int64),
            priority_point_ids=cp.asarray(priority_columns["point_id"], dtype=cp.int64),
            priority_face_ids=cp.asarray(priority_columns["face_id"], dtype=cp.int64),
            priorities=cp.asarray(priority_columns["priority"], dtype=cp.int64),
            candidate_point_ids=cp.asarray((1, 1, 2), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100, 101, 102), dtype=cp.int64),
            topology_shape_ids=cp.asarray((100, 101, 102), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((10, 20, 30), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((11, 21, 31), dtype=cp.int64),
        )
        codes = actual["selection_status_code_labels"]

        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["shape_id"]), expected["shape_id"])
        self.assertEqual(_host_tuple(actual["membership"]), expected["membership"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["selection_point_id"]), (1, 2))
        self.assertEqual(_host_tuple(actual["selection_owner_face_id"]), (20, 30))
        self.assertEqual(
            _host_tuple(actual["selection_status_code"]),
            (codes["priority_tie_break"], codes["unique_max_incident_face"]),
        )

    def test_cupy_pipeline_can_drop_unresolved_owner_before_filter(self):
        cp = _cupy_or_skip(self)
        actual = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            incident_face_ids=cp.asarray((10, 20), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
            priority_point_ids=cp.asarray((), dtype=cp.int64),
            priority_face_ids=cp.asarray((), dtype=cp.int64),
            priorities=cp.asarray((), dtype=cp.int64),
            candidate_point_ids=cp.asarray((1,), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_shape_ids=cp.asarray((100,), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((10,), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((20,), dtype=cp.int64),
            ambiguity_policy="drop",
            missing_owner_policy="drop",
        )

        self.assertEqual(_host_tuple(actual["point_id"]), ())
        self.assertEqual(_host_tuple(actual["selection_point_id"]), ())

    def test_report_keeps_composed_pipeline_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("composed CuPy device-column pipeline", text)
        self.assertIn("selection plus membership filter", text)
        self.assertIn("not native RT traversal", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 30 tests in 0.830s", text)
        self.assertIn("Ran 89 tests in 0.760s", text)


if __name__ == "__main__":
    unittest.main()
