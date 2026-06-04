import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
INCIDENT_ARTIFACT = ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3349_owner_face_priority_pipeline_contract_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


class Goal3349OwnerFacePriorityPipelineContractTest(unittest.TestCase):
    def test_contract_is_exported_and_strictly_bounded(self):
        self.assertEqual(
            rt.OWNER_FACE_PRIORITY_PIPELINE_CONTRACT,
            "rtdl.closed_shape.owner_face_priority_pipeline.v1",
        )
        contract = rt.validate_owner_face_priority_pipeline_contract()

        self.assertEqual(contract["status"], "python_reference_contract_only")
        self.assertTrue(contract["app_agnostic"])
        self.assertTrue(contract["caller_policy_required"])
        self.assertFalse(contract["native_engine_may_infer_app_ownership"])
        self.assertFalse(contract["selection_rule"]["native_engine_may_invent_priority"])
        self.assertTrue(any("priority_rows" in item for item in contract["inputs"]))
        self.assertTrue(all(value is False for value in contract["claim_boundary"].values()))

    def test_contract_names_actual_reference_steps(self):
        contract = rt.owner_face_priority_pipeline_contract()
        self.assertEqual(
            contract["pipeline_steps"],
            (
                "select_owner_faces_from_incident_candidates_with_priority",
                "owner_face_ids_by_point_from_selection_rows",
                "filter_closed_shape_membership_candidates_by_owner_face",
            ),
        )
        for name in contract["pipeline_steps"]:
            self.assertTrue(callable(getattr(rt, name)))

    def test_reference_pipeline_still_recovers_known_owner_face_rows(self):
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

    def test_report_explains_the_boundary(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("OWNER_FACE_PRIORITY_PIPELINE_CONTRACT", text)
        self.assertIn("caller/data priority rows are mandatory", text)
        self.assertIn("native engine must not infer", text)
        self.assertIn("does not authorize release", text)
        self.assertIn("blocked_until_contract_stable_and_validated", text)


if __name__ == "__main__":
    unittest.main()
