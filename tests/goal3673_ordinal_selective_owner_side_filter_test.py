from __future__ import annotations

import unittest
import json
from pathlib import Path

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3673_ordinal_selective_owner_side_filter_2026-06-06.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3673_rayjoin_ordinal_owner_side_probe_a5000"
ALL_POINT_ARTIFACT = ARTIFACT_DIR / "full_county_ordinal_owner_side_route_probe.json"
SELECTIVE_ARTIFACT = ARTIFACT_DIR / "full_county_selective_ordinal_owner_side_route_probe.json"
GEMINI_REVIEW = (
    ROOT
    / "docs/reviews/goal3674_gemini_review_goal3673_ordinal_selective_owner_side_filter_2026-06-06.md"
)


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


class Goal3673OrdinalSelectiveOwnerSideFilterTest(unittest.TestCase):
    def test_selective_side_filter_preserves_non_selected_duplicate_id_rows(self) -> None:
        cp = _cupy_or_skip(self)

        actual = rt.run_selective_closed_shape_owner_face_side_membership_pipeline_cupy(
            candidate_point_ids=cp.asarray((7, 7, 7, 7), dtype=cp.int64),
            candidate_shape_ids=cp.asarray((16312, 891, 891, 16312), dtype=cp.int64),
            candidate_point_ordinals=cp.asarray((0, 0, 1, 1), dtype=cp.int64),
            candidate_shape_ordinals=cp.asarray((1, 0, 0, 1), dtype=cp.int64),
            selected_point_ordinals=cp.asarray((1,), dtype=cp.int64),
            topology_shape_ids=cp.asarray((891, 16312), dtype=cp.int64),
            topology_shape_ordinals=cp.asarray((0, 1), dtype=cp.int64),
            topology_left_face_ids=cp.asarray((371, 384), dtype=cp.int64),
            topology_right_face_ids=cp.asarray((384, 607), dtype=cp.int64),
            owner_point_ids=cp.asarray((7, 7), dtype=cp.int64),
            owner_point_ordinals=cp.asarray((0, 1), dtype=cp.int64),
            owner_face_ids=cp.asarray((371, 384), dtype=cp.int64),
            owner_side_codes=("left", "right"),
        )

        self.assertEqual(_host_tuple(actual["point_id"]), (7, 7, 7))
        self.assertEqual(_host_tuple(actual["shape_id"]), (891, 16312, 891))
        self.assertEqual(_host_tuple(actual["point_ordinal"]), (0, 0, 1))
        self.assertEqual(_host_tuple(actual["shape_ordinal"]), (0, 1, 0))
        self.assertEqual(_host_tuple(actual["owner_face_id"]), (-1, -1, 384))
        self.assertEqual(_host_tuple(actual["owner_side_code"]), (-1, -1, 1))
        self.assertEqual(actual["selected_candidate_row_count"], 2)
        self.assertEqual(actual["passthrough_candidate_row_count"], 2)
        self.assertEqual(actual["selected_filter_key_mode"], "input_ordinal")

    def test_contract_lists_selective_side_aware_helper_and_ordinal_policy(self) -> None:
        contract = rt.validate_owner_face_priority_pipeline_contract()
        helpers = contract["optional_columnar_pipeline_helpers"]
        policy = contract["filter_policy"]

        self.assertIn(
            "run_selective_closed_shape_owner_face_side_membership_pipeline_cupy",
            helpers,
        )
        self.assertEqual(
            policy["side_aware_filter_owner_identity"],
            "public_point_id_by_default_or_input_ordinal_when_supplied",
        )
        self.assertEqual(
            policy["side_aware_filter_topology_identity"],
            "public_shape_id_by_default_or_prepared_shape_ordinal_when_supplied",
        )

    def test_report_and_artifacts_record_selective_repair_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        all_point = json.loads(ALL_POINT_ARTIFACT.read_text(encoding="utf-8"))
        selective = json.loads(SELECTIVE_ARTIFACT.read_text(encoding="utf-8"))

        self.assertIn("not a universal replacement for membership", report)
        self.assertIn("selective ordinal-aware side filter", report)
        self.assertFalse(all_point["matches_exact_multiset"])
        self.assertEqual(all_point["filtered_row_count"], 22639)
        self.assertEqual(all_point["after_missing_count"], 24623)
        self.assertTrue(selective["matches_exact_multiset"])
        self.assertEqual(selective["candidate_native_row_count"], 47264)
        self.assertEqual(selective["filtered_row_count"], 47262)
        self.assertEqual(selective["exact_row_count"], 47262)
        self.assertEqual(selective["selected_point_ordinals"], [892, 893])
        self.assertEqual(selective["selected_candidate_row_count"], 4)
        self.assertEqual(selective["passthrough_candidate_row_count"], 47260)
        self.assertEqual(
            selective["removed_extra_rows"],
            [[893, 16312], [894, 16312]],
        )
        self.assertFalse(any(selective["claim_boundary"].values()))

    def test_gemini_review_accepts_with_boundary(self) -> None:
        text = GEMINI_REVIEW.read_text(encoding="utf-8")

        self.assertIn("`accept-with-boundary`", text)
        self.assertIn("does *not* authorize automatic default route selection", text)
        self.assertIn("generic, caller-defined ambiguity-set derivation contract", text)


if __name__ == "__main__":
    unittest.main()
