from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3671_side_aware_owner_face_filter_2026-06-06.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3671_rayjoin_topology_probe_a5000"
    / "full_county_side_aware_route_probe.json"
)


TOPOLOGY_ROWS = (
    {
        "shape_id": 891,
        "left_face_id": 371,
        "right_face_id": 384,
        "has_left_face": 1,
        "has_right_face": 1,
    },
    {
        "shape_id": 16312,
        "left_face_id": 384,
        "right_face_id": 607,
        "has_left_face": 1,
        "has_right_face": 1,
    },
)


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3671SideAwareOwnerFaceFilterTest(unittest.TestCase):
    def test_row_filter_distinguishes_same_face_on_opposite_sides(self) -> None:
        candidate_rows = (
            {"point_id": 893, "shape_id": 891},
            {"point_id": 893, "shape_id": 16312},
            {"point_id": 894, "shape_id": 891},
            {"point_id": 894, "shape_id": 16312},
        )

        face_only = rt.filter_closed_shape_membership_candidates_by_owner_face(
            candidate_rows,
            TOPOLOGY_ROWS,
            {893: 371, 894: 384},
        )
        side_aware = rt.filter_closed_shape_membership_candidates_by_owner_face_side(
            candidate_rows,
            TOPOLOGY_ROWS,
            {
                893: (371, "left"),
                894: (384, "right"),
            },
        )

        self.assertEqual(
            tuple((row["point_id"], row["shape_id"]) for row in face_only),
            ((893, 891), (894, 891), (894, 16312)),
        )
        self.assertEqual(
            tuple((row["point_id"], row["shape_id"], row["owner_side"]) for row in side_aware),
            ((893, 891, "left"), (894, 891, "right")),
        )

    def test_columnar_filter_preserves_duplicate_candidate_rows(self) -> None:
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(
            candidate_point_ids=(894, 894, 894),
            candidate_shape_ids=(891, 891, 16312),
            topology_shape_ids=(891, 16312),
            topology_left_face_ids=(371, 384),
            topology_right_face_ids=(384, 607),
            owner_point_ids=(894,),
            owner_face_ids=(384,),
            owner_side_codes=("right",),
        )

        self.assertEqual(actual["point_id"], (894, 894))
        self.assertEqual(actual["shape_id"], (891, 891))
        self.assertEqual(actual["owner_side"], ("right", "right"))

    def test_cupy_filter_matches_columnar_reference(self) -> None:
        cp = _cupy_or_skip(self)
        expected = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(
            candidate_point_ids=(893, 893, 894, 894),
            candidate_shape_ids=(891, 16312, 891, 16312),
            topology_shape_ids=(891, 16312),
            topology_left_face_ids=(371, 384),
            topology_right_face_ids=(384, 607),
            owner_point_ids=(893, 894),
            owner_face_ids=(371, 384),
            owner_side_codes=("left", "right"),
        )
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_cupy(
            candidate_point_ids=cp.asarray((893, 893, 894, 894), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((891, 16312, 891, 16312), dtype=cp.int64),
            topology_shape_ids=cp.asarray((891, 16312), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((371, 384), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((384, 607), dtype=cp.int64),
            owner_point_ids=cp.asarray((893, 894), dtype=cp.int64),
            owner_face_ids=cp.asarray((371, 384), dtype=cp.int64),
            owner_side_codes=("left", "right"),
        )

        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["shape_id"]), expected["shape_id"])
        self.assertEqual(_host_tuple(actual["membership"]), expected["membership"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["owner_side_code"]), expected["owner_side_code"])

    def test_contract_and_report_record_major_direction_not_closeout(self) -> None:
        contract = rt.validate_owner_face_priority_pipeline_contract()
        helpers = contract["optional_columnar_pipeline_helpers"]
        policy = contract["filter_policy"]

        self.assertIn(
            "filter_closed_shape_membership_candidate_columns_by_owner_face_side_cupy",
            helpers,
        )
        self.assertEqual(
            policy["side_aware_filter_candidate_duplicates"],
            "preserve_row_stream_multiplicity",
        )
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3668 is superseded", text)
        self.assertIn("v2.9 remains open", text)
        self.assertIn("side-aware topology ownership", text)
        self.assertIn("not minor tuning", text)
        self.assertIn("47264 != 47262", text)

    def test_pod_artifact_records_full_county_side_aware_repair(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            data["schema"],
            "rtdl.goal3671.rayjoin_full_county_side_aware_route_probe.v1",
        )
        self.assertEqual(data["exact_row_count"], 47262)
        self.assertEqual(data["candidate_native_row_count"], 47264)
        self.assertEqual(data["filtered_row_count"], 47262)
        self.assertEqual(data["before_extra_count"], 2)
        self.assertEqual(data["after_extra_count"], 0)
        self.assertEqual(data["after_missing_count"], 0)
        self.assertTrue(data["matches_exact_multiset"])
        self.assertEqual(data["selected_point_ids"], [893, 894])
        self.assertEqual(data["selected_candidate_row_count"], 4)
        self.assertEqual(data["selected_filtered_row_count"], 2)
        self.assertEqual(data["removed_extra_rows"], [[893, 16312], [894, 16312]])
        self.assertFalse(any(data["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
