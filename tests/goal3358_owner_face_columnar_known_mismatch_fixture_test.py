import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3358_owner_face_columnar_known_mismatch_fixture_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


class Goal3358OwnerFaceColumnarKnownMismatchFixtureTest(unittest.TestCase):
    def _build_fixture_columns(self):
        topology = json.loads(TOPOLOGY_ARTIFACT.read_text(encoding="utf-8"))
        incident = json.loads(INCIDENT_ARTIFACT.read_text(encoding="utf-8"))

        incident_point_ids = []
        incident_face_ids = []
        incident_counts = []
        rank0 = []
        for item in incident["rows"]:
            point_id = int(item["point_id"])
            owner_face = OWNER_FACE_BY_POINT[point_id]
            for entry in item["endpoint_face_frequency"]:
                face_id = int(entry["face_id"])
                incident_point_ids.append(point_id)
                incident_face_ids.append(face_id)
                incident_counts.append(int(entry["count"]))
                rank0.append(0 if face_id == owner_face else 10 + face_id)

        candidate_point_ids = []
        candidate_shape_ids = []
        exact_by_point = {}
        for item in topology["per_mismatch_point"]:
            point_id = int(item["point_id"])
            exact_by_point[point_id] = tuple(int(shape_id) for shape_id in item["exact_shape_ids"])
            for shape_id in sorted(set(item["exact_shape_ids"]) | set(item["extra_shape_ids"])):
                candidate_point_ids.append(point_id)
                candidate_shape_ids.append(int(shape_id))

        topology_rows = topology["shape_topology_rows"]
        return {
            "incident_point_ids": tuple(incident_point_ids),
            "incident_face_ids": tuple(incident_face_ids),
            "incident_counts": tuple(incident_counts),
            "rank_columns": {"rank0": tuple(rank0)},
            "candidate_point_ids": tuple(candidate_point_ids),
            "candidate_shape_ids": tuple(candidate_shape_ids),
            "topology_shape_ids": tuple(int(row.get("shape_id", row["chain_id"])) for row in topology_rows),
            "topology_left_face_ids": tuple(int(row["left_face_id"]) for row in topology_rows),
            "topology_right_face_ids": tuple(int(row["right_face_id"]) for row in topology_rows),
            "topology_has_left_faces": tuple(int(row.get("has_left_face", 1)) for row in topology_rows),
            "topology_has_right_faces": tuple(int(row.get("has_right_face", 1)) for row in topology_rows),
            "exact_by_point": exact_by_point,
        }

    def test_complete_columnar_pipeline_recovers_known_exact_rows(self):
        fixture = self._build_fixture_columns()

        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=fixture["incident_point_ids"],
            face_ids=fixture["incident_face_ids"],
            rank_columns=fixture["rank_columns"],
            rank_fields=("rank0",),
        )
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=fixture["incident_point_ids"],
            incident_face_ids=fixture["incident_face_ids"],
            incident_face_counts=fixture["incident_counts"],
            priority_point_ids=priority_columns["point_id"],
            priority_face_ids=priority_columns["face_id"],
            priorities=priority_columns["priority"],
        )
        self.assertEqual(
            dict(zip(selected_columns["point_id"], selected_columns["owner_face_id"])),
            OWNER_FACE_BY_POINT,
        )

        filtered_columns = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=fixture["candidate_point_ids"],
            candidate_shape_ids=fixture["candidate_shape_ids"],
            topology_shape_ids=fixture["topology_shape_ids"],
            topology_left_face_ids=fixture["topology_left_face_ids"],
            topology_right_face_ids=fixture["topology_right_face_ids"],
            topology_has_left_faces=fixture["topology_has_left_faces"],
            topology_has_right_faces=fixture["topology_has_right_faces"],
            owner_point_ids=selected_columns["point_id"],
            owner_face_ids=selected_columns["owner_face_id"],
        )

        filtered_by_point = {}
        for point_id, shape_id in zip(filtered_columns["point_id"], filtered_columns["shape_id"]):
            filtered_by_point.setdefault(int(point_id), []).append(int(shape_id))

        self.assertEqual(set(filtered_by_point), set(fixture["exact_by_point"]))
        for point_id, exact_shape_ids in fixture["exact_by_point"].items():
            self.assertEqual(tuple(sorted(filtered_by_point[point_id])), exact_shape_ids)

    def test_columnar_fixture_matches_row_reference(self):
        fixture = self._build_fixture_columns()
        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=fixture["incident_point_ids"],
            face_ids=fixture["incident_face_ids"],
            rank_columns=fixture["rank_columns"],
            rank_fields=("rank0",),
        )
        selected_columns = rt.select_owner_faces_from_incident_candidate_columns_with_priority_columns(
            incident_point_ids=fixture["incident_point_ids"],
            incident_face_ids=fixture["incident_face_ids"],
            incident_face_counts=fixture["incident_counts"],
            priority_point_ids=priority_columns["point_id"],
            priority_face_ids=priority_columns["face_id"],
            priorities=priority_columns["priority"],
        )
        columnar_filtered = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
            candidate_point_ids=fixture["candidate_point_ids"],
            candidate_shape_ids=fixture["candidate_shape_ids"],
            topology_shape_ids=fixture["topology_shape_ids"],
            topology_left_face_ids=fixture["topology_left_face_ids"],
            topology_right_face_ids=fixture["topology_right_face_ids"],
            topology_has_left_faces=fixture["topology_has_left_faces"],
            topology_has_right_faces=fixture["topology_has_right_faces"],
            owner_point_ids=selected_columns["point_id"],
            owner_face_ids=selected_columns["owner_face_id"],
        )

        row_filtered = rt.filter_closed_shape_membership_candidates_by_owner_face(
            (
                {"point_id": point_id, "shape_id": shape_id}
                for point_id, shape_id in zip(fixture["candidate_point_ids"], fixture["candidate_shape_ids"])
            ),
            (
                {
                    "chain_id": shape_id,
                    "left_face_id": left_face_id,
                    "right_face_id": right_face_id,
                    "has_left_face": has_left,
                    "has_right_face": has_right,
                }
                for shape_id, left_face_id, right_face_id, has_left, has_right in zip(
                    fixture["topology_shape_ids"],
                    fixture["topology_left_face_ids"],
                    fixture["topology_right_face_ids"],
                    fixture["topology_has_left_faces"],
                    fixture["topology_has_right_faces"],
                )
            ),
            OWNER_FACE_BY_POINT,
        )

        self.assertEqual(
            columnar_filtered,
            {
                "point_id": tuple(row["point_id"] for row in row_filtered),
                "shape_id": tuple(row["shape_id"] for row in row_filtered),
                "membership": tuple(row["membership"] for row in row_filtered),
                "owner_face_id": tuple(row["owner_face_id"] for row in row_filtered),
            },
        )

    def test_report_keeps_fixture_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("seven known county mismatch points", text)
        self.assertIn("same-contract fixture", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("not a native/device implementation", text)


if __name__ == "__main__":
    unittest.main()
