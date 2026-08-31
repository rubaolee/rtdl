from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3380_selective_owner_face_cupy_pipeline_2026-06-04.md"


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(cp_module, array):
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


class Goal3380SelectiveOwnerFaceCupyPipelineTest(unittest.TestCase):
    def test_selective_pipeline_filters_selected_points_and_passes_through_others(self):
        cp = _cupy_or_skip(self)

        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=(1, 1),
            face_ids=(100, 300),
            rank_columns={"rank0": (0, 1)},
            rank_fields=("rank0",),
        )
        actual = rt.run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray((1, 1), dtype=cp.int64),
            incident_face_ids=cp.asarray((100, 300), dtype=cp.int64),
            incident_face_counts=cp.asarray((2, 2), dtype=cp.int64),
            priority_point_ids=cp.asarray(priority_columns["point_id"], dtype=cp.int64),
            priority_face_ids=cp.asarray(priority_columns["face_id"], dtype=cp.int64),
            priorities=cp.asarray(priority_columns["priority"], dtype=cp.int64),
            candidate_point_ids=cp.asarray((1, 1, 2, 2), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((10, 20, 30, 40), dtype=cp.int64),
            topology_shape_ids=cp.asarray((10, 20, 30, 40), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((100, 300, 500, 700), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((200, 400, 600, 800), dtype=cp.int64),
            selected_point_ids=cp.asarray((1,), dtype=cp.int64),
        )

        self.assertEqual(_host_tuple(cp, actual["point_id"]), (1, 2, 2))
        self.assertEqual(_host_tuple(cp, actual["shape_id"]), (10, 30, 40))
        self.assertEqual(_host_tuple(cp, actual["membership"]), (1, 1, 1))
        self.assertEqual(_host_tuple(cp, actual["owner_face_id"]), (100, -1, -1))
        self.assertEqual(_host_tuple(cp, actual["selection_point_id"]), (1,))
        self.assertEqual(_host_tuple(cp, actual["selection_owner_face_id"]), (100,))
        self.assertEqual(actual["selected_candidate_row_count"], 2)
        self.assertEqual(actual["passthrough_candidate_row_count"], 2)
        self.assertEqual(actual["selected_point_filter_mode"], "caller_supplied_ambiguity_set")

    def test_contract_and_report_document_selective_boundary(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy",
            contract["optional_columnar_pipeline_helpers"],
        )
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("caller supplies `selected_point_ids`", text)
        self.assertIn("does not infer which points are ambiguous", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("native default route claims", text)


if __name__ == "__main__":
    unittest.main()
