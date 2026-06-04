from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "src" / "rtdsl" / "datasets.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
REPORT = ROOT / "docs" / "reports" / "goal3326_cdb_topology_rows_for_future_closed_shape_contract_2026-06-04.md"


class Goal3326CdbTopologyRowsTest(unittest.TestCase):
    def test_chains_to_topology_rows_preserves_generic_face_columns(self) -> None:
        dataset = rt.parse_cdb_text(
            "\n".join(
                [
                    "1 3 10 12 0 7",
                    "0 0",
                    "1 0",
                    "0 0",
                    "2 4 20 23 9 0",
                    "0 1",
                    "1 1",
                    "1 2",
                    "0 1",
                ]
            ),
            name="mini_topology",
        )

        rows = rt.chains_to_topology_rows(dataset)

        self.assertEqual(
            rows,
            (
                {
                    "chain_id": 1,
                    "point_count": 3,
                    "first_point_id": 10,
                    "last_point_id": 12,
                    "left_face_id": 0,
                    "right_face_id": 7,
                    "has_left_face": 0,
                    "has_right_face": 1,
                },
                {
                    "chain_id": 2,
                    "point_count": 4,
                    "first_point_id": 20,
                    "last_point_id": 23,
                    "left_face_id": 9,
                    "right_face_id": 0,
                    "has_left_face": 1,
                    "has_right_face": 0,
                },
            ),
        )

    def test_limit_chains_and_exports_are_available(self) -> None:
        dataset = rt.parse_cdb_text(
            "\n".join(
                [
                    "1 3 1 3 4 0",
                    "0 0",
                    "1 0",
                    "0 0",
                    "2 3 4 6 5 0",
                    "0 1",
                    "1 1",
                    "0 1",
                ]
            ),
            name="mini_limit",
        )
        self.assertEqual(len(rt.chains_to_topology_rows(dataset, limit_chains=1)), 1)
        self.assertIn("chains_to_topology_rows", INIT.read_text(encoding="utf-8"))

    def test_helper_is_documented_as_metadata_not_membership_classifier(self) -> None:
        datasets = DATASETS.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("def chains_to_topology_rows", datasets)
        self.assertIn("do not reconstruct faces", datasets)
        self.assertIn("does not reconstruct faces, classify point membership", report)
        self.assertIn("rtdl_beats_rayjoin_claim_authorized`: false", report)


if __name__ == "__main__":
    unittest.main()

