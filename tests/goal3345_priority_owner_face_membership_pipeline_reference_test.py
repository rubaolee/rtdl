import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3345_priority_owner_face_membership_pipeline_reference_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


class Goal3345PriorityOwnerFaceMembershipPipelineReferenceTest(unittest.TestCase):
    def test_priority_selected_owner_faces_filter_candidates_to_exact_rows(self):
        topology = json.loads(TOPOLOGY_ARTIFACT.read_text(encoding="utf-8"))
        incident = json.loads(INCIDENT_ARTIFACT.read_text(encoding="utf-8"))

        incident_candidates = []
        priority_rows = []
        for item in incident["rows"]:
            point_id = int(item["point_id"])
            owner_face = OWNER_FACE_BY_POINT[point_id]
            for entry in item["endpoint_face_frequency"]:
                face_id = int(entry["face_id"])
                incident_candidates.append(
                    {
                        "point_id": point_id,
                        "face_id": face_id,
                        "incident_face_count": int(entry["count"]),
                    }
                )
                priority_rows.append(
                    {
                        "point_id": point_id,
                        "face_id": face_id,
                        "priority": 0 if face_id == owner_face else 10,
                    }
                )

        selected = rt.select_owner_faces_from_incident_candidates_with_priority(
            incident_candidates,
            priority_rows,
        )
        owner_faces = rt.owner_face_ids_by_point_from_selection_rows(selected)
        self.assertEqual(owner_faces, OWNER_FACE_BY_POINT)

        candidate_rows = []
        exact_by_point = {}
        for item in topology["per_mismatch_point"]:
            point_id = int(item["point_id"])
            exact_by_point[point_id] = list(item["exact_shape_ids"])
            for shape_id in sorted(set(item["exact_shape_ids"]) | set(item["extra_shape_ids"])):
                candidate_rows.append({"point_id": point_id, "shape_id": int(shape_id)})

        filtered = rt.filter_closed_shape_membership_candidates_by_owner_face(
            candidate_rows,
            topology["shape_topology_rows"],
            owner_faces,
        )
        filtered_by_point = {}
        for row in filtered:
            filtered_by_point.setdefault(int(row["point_id"]), []).append(int(row["shape_id"]))

        self.assertEqual(set(filtered_by_point), set(exact_by_point))
        for point_id, exact_shape_ids in exact_by_point.items():
            self.assertEqual(sorted(filtered_by_point[point_id]), exact_shape_ids)

    def test_mapping_helper_rejects_ambiguous_or_conflicting_rows(self):
        with self.assertRaisesRegex(ValueError, "not selected"):
            rt.owner_face_ids_by_point_from_selection_rows(
                ({"point_id": 1, "owner_face_id": -1},)
            )
        self.assertEqual(
            rt.owner_face_ids_by_point_from_selection_rows(
                ({"point_id": 1, "owner_face_id": -1},),
                require_selected=False,
            ),
            {},
        )
        with self.assertRaisesRegex(ValueError, "conflicting owner face"):
            rt.owner_face_ids_by_point_from_selection_rows(
                (
                    {"point_id": 1, "owner_face_id": 10},
                    {"point_id": 1, "owner_face_id": 20},
                )
            )

    def test_report_keeps_pipeline_claim_bounded(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not automatic RayJoin support", text)
        self.assertIn("must not invent the priority rows", text)
        self.assertIn("remains blocked outside validated domains", text)


if __name__ == "__main__":
    unittest.main()
