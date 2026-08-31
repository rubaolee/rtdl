from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3351_owner_face_priority_rank_signal_derivation_2026-06-04.md"


class Goal3351OwnerFacePriorityRankSignalDerivationTest(unittest.TestCase):
    def test_lower_rank_tuple_becomes_lower_priority(self):
        rows = (
            {"point_id": 1, "face_id": 10, "rank0": 1, "rank1": 0},
            {"point_id": 1, "face_id": 20, "rank0": 0, "rank1": 5},
            {"point_id": 1, "face_id": 30, "rank0": 2, "rank1": 0},
            {"point_id": 2, "face_id": 40, "rank0": 3, "rank1": 1},
        )
        priority_rows = rt.derive_owner_face_priority_rows_from_rank_signals(
            rows,
            rank_fields=("rank0", "rank1"),
        )

        self.assertEqual(
            priority_rows,
            (
                {"point_id": 1, "face_id": 20, "priority": 0, "priority_rank_key": (0, 5)},
                {"point_id": 1, "face_id": 10, "priority": 1, "priority_rank_key": (1, 0)},
                {"point_id": 1, "face_id": 30, "priority": 2, "priority_rank_key": (2, 0)},
                {"point_id": 2, "face_id": 40, "priority": 0, "priority_rank_key": (3, 1)},
            ),
        )

    def test_derived_priorities_feed_existing_owner_face_selector(self):
        incident_rows = (
            {"point_id": 1, "face_id": 10, "incident_face_count": 2},
            {"point_id": 1, "face_id": 20, "incident_face_count": 2},
        )
        signal_rows = (
            {"point_id": 1, "face_id": 10, "rank0": 5},
            {"point_id": 1, "face_id": 20, "rank0": 1},
        )
        priority_rows = rt.derive_owner_face_priority_rows_from_rank_signals(
            signal_rows,
            rank_fields=("rank0",),
        )
        selected = rt.select_owner_faces_from_incident_candidates_with_priority(
            incident_rows,
            priority_rows,
        )

        self.assertEqual(
            selected,
            (
                {
                    "point_id": 1,
                    "owner_face_id": 20,
                    "incident_face_count": 2,
                    "candidate_count": 2,
                    "selection_status": "priority_tie_break",
                },
            ),
        )

    def test_derivation_fails_closed_on_missing_duplicate_or_tied_rank(self):
        with self.assertRaisesRegex(ValueError, "rank_fields"):
            rt.derive_owner_face_priority_rows_from_rank_signals(
                ({"point_id": 1, "face_id": 10, "rank0": 1},),
                rank_fields=(),
            )
        with self.assertRaisesRegex(KeyError, "missing owner-face priority rank fields"):
            rt.derive_owner_face_priority_rows_from_rank_signals(
                ({"point_id": 1, "face_id": 10},),
                rank_fields=("rank0",),
            )
        with self.assertRaisesRegex(ValueError, "duplicate owner-face priority signal"):
            rt.derive_owner_face_priority_rows_from_rank_signals(
                (
                    {"point_id": 1, "face_id": 10, "rank0": 1},
                    {"point_id": 1, "face_id": 10, "rank0": 2},
                ),
                rank_fields=("rank0",),
            )
        with self.assertRaisesRegex(ValueError, "ambiguous owner-face priority rank"):
            rt.derive_owner_face_priority_rows_from_rank_signals(
                (
                    {"point_id": 1, "face_id": 10, "rank0": 1},
                    {"point_id": 1, "face_id": 20, "rank0": 1},
                ),
                rank_fields=("rank0",),
            )

    def test_drop_policy_leaves_tied_priorities_unselected(self):
        priority_rows = rt.derive_owner_face_priority_rows_from_rank_signals(
            (
                {"point_id": 1, "face_id": 10, "rank0": 1},
                {"point_id": 1, "face_id": 20, "rank0": 1},
                {"point_id": 1, "face_id": 30, "rank0": 2},
            ),
            rank_fields=("rank0",),
            tie_policy="drop",
        )

        self.assertEqual(
            priority_rows,
            ({"point_id": 1, "face_id": 30, "priority": 0, "priority_rank_key": (2,)},),
        )

    def test_contract_mentions_optional_derivation_helper(self):
        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "derive_owner_face_priority_rows_from_rank_signals",
            contract["optional_priority_derivation_helpers"],
        )

    def test_report_keeps_derivation_policy_outside_engine(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("caller-supplied rank signals", text)
        self.assertIn("does not infer ownership", text)
        self.assertIn("missing, duplicate, or tied evidence fails closed", text)
        self.assertIn("does not authorize release", text)


if __name__ == "__main__":
    unittest.main()
