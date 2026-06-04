import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3369_owner_face_cupy_real_fixture_pipeline_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


def _cupy_or_skip(test_case):
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:
        test_case.skipTest(f"CuPy is not available: {exc}")
    return cp


def _host_tuple(array):
    return tuple(int(value) for value in array.get().tolist())


def _build_fixture_columns():
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


class Goal3369OwnerFaceCupyRealFixturePipelineTest(unittest.TestCase):
    def test_composed_cupy_pipeline_recovers_known_real_fixture_rows(self):
        cp = _cupy_or_skip(self)
        fixture = _build_fixture_columns()
        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=fixture["incident_point_ids"],
            face_ids=fixture["incident_face_ids"],
            rank_columns=fixture["rank_columns"],
            rank_fields=("rank0",),
        )
        expected = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray(fixture["incident_point_ids"], dtype=cp.int64),
            incident_face_ids=cp.asarray(fixture["incident_face_ids"], dtype=cp.int64),
            incident_face_counts=cp.asarray(fixture["incident_counts"], dtype=cp.int64),
            priority_point_ids=cp.asarray(priority_columns["point_id"], dtype=cp.int64),
            priority_face_ids=cp.asarray(priority_columns["face_id"], dtype=cp.int64),
            priorities=cp.asarray(priority_columns["priority"], dtype=cp.int64),
            candidate_point_ids=cp.asarray(fixture["candidate_point_ids"], dtype=cp.int64),
            candidate_shape_ids=cp.asarray(fixture["candidate_shape_ids"], dtype=cp.int64),
            topology_shape_ids=cp.asarray(fixture["topology_shape_ids"], dtype=cp.int64),
            topology_left_face_ids=cp.asarray(fixture["topology_left_face_ids"], dtype=cp.int64),
            topology_right_face_ids=cp.asarray(fixture["topology_right_face_ids"], dtype=cp.int64),
            topology_has_left_faces=cp.asarray(fixture["topology_has_left_faces"], dtype=cp.int8),
            topology_has_right_faces=cp.asarray(fixture["topology_has_right_faces"], dtype=cp.int8),
        )

        filtered_by_point = {}
        for point_id, shape_id in zip(_host_tuple(expected["point_id"]), _host_tuple(expected["shape_id"])):
            filtered_by_point.setdefault(point_id, []).append(shape_id)

        self.assertEqual(set(filtered_by_point), set(fixture["exact_by_point"]))
        for point_id, exact_shape_ids in fixture["exact_by_point"].items():
            self.assertEqual(tuple(sorted(filtered_by_point[point_id])), exact_shape_ids)
        self.assertEqual(
            dict(zip(_host_tuple(expected["selection_point_id"]), _host_tuple(expected["selection_owner_face_id"]))),
            OWNER_FACE_BY_POINT,
        )

    def test_report_keeps_real_fixture_boundary_visible(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("seven known county mismatch points", text)
        self.assertIn("composed CuPy device-column pipeline", text)
        self.assertIn("not native RT traversal", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Ran 14 tests in 0.765s", text)
        self.assertIn("Ran 96 tests in 0.782s", text)


if __name__ == "__main__":
    unittest.main()
