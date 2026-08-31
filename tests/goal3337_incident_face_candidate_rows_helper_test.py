import unittest

import rtdsl as rt
from rtdsl.datasets import CdbChain
from rtdsl.datasets import CdbDataset
from rtdsl.datasets import CdbPoint


def _chain(chain_id, left, right, points):
    return CdbChain(
        chain_id=chain_id,
        point_count=len(points),
        first_point_id=chain_id * 10,
        last_point_id=chain_id * 10 + len(points) - 1,
        left_face_id=left,
        right_face_id=right,
        points=tuple(CdbPoint(float(x), float(y)) for x, y in points),
    )


class Goal3337IncidentFaceCandidateRowsHelperTest(unittest.TestCase):
    def test_incident_faces_are_counted_without_selecting_owner(self):
        dataset = CdbDataset(
            name="synthetic",
            chains=(
                _chain(1, 10, 20, [(0, 0), (1, 0)]),
                _chain(2, 10, 30, [(0, 0), (0, 1)]),
                _chain(3, 20, 30, [(0, 0), (-1, 0)]),
                _chain(4, 40, 0, [(5, 5), (6, 6)]),
            ),
        )
        rows = rt.chains_to_incident_face_candidate_rows(dataset, point_chain_ids={1})
        self.assertEqual(
            [(row["face_id"], row["incident_face_count"], row["incident_chain_count"]) for row in rows],
            [(10, 2, 3), (20, 2, 3), (30, 2, 3)],
        )
        self.assertEqual({row["point_id"] for row in rows}, {1})
        self.assertEqual({row["probe_x"] for row in rows}, {0.0})
        self.assertEqual({row["probe_y"] for row in rows}, {0.0})

    def test_filtering_and_precision_are_explicit(self):
        dataset = CdbDataset(
            name="synthetic",
            chains=(
                _chain(1, 1, 2, [(0.00000000004, 0), (1, 0)]),
                _chain(2, 1, 3, [(0.00000000005, 0), (0, 1)]),
                _chain(3, 4, 5, [(9, 9), (10, 10)]),
            ),
        )
        rows = rt.chains_to_incident_face_candidate_rows(
            dataset,
            point_chain_ids=(1,),
            coordinate_precision=9,
        )
        self.assertEqual([row["face_id"] for row in rows], [1, 2, 3])
        self.assertEqual([row["incident_face_count"] for row in rows], [2, 1, 1])
        with self.assertRaises(ValueError):
            rt.chains_to_incident_face_candidate_rows(dataset, coordinate_precision=-1)


if __name__ == "__main__":
    unittest.main()
