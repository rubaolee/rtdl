import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3330_owner_face_closed_shape_membership_reference_contract_2026-06-04.md"


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


class Goal3330OwnerFaceClosedShapeMembershipReferenceContractTest(unittest.TestCase):
    def _artifact_rows(self):
        data = json.loads(TOPOLOGY_ARTIFACT.read_text(encoding="utf-8"))
        topology_rows = data["shape_topology_rows"]
        candidate_rows = []
        exact_by_point = {}
        for item in data["per_mismatch_point"]:
            point_id = int(item["point_id"])
            exact_by_point[point_id] = list(item["exact_shape_ids"])
            device_shape_ids = sorted(set(item["exact_shape_ids"]) | set(item["extra_shape_ids"]))
            for shape_id in device_shape_ids:
                candidate_rows.append({"point_id": point_id, "shape_id": int(shape_id)})
        return topology_rows, candidate_rows, exact_by_point

    def test_owner_face_filter_reconciles_known_county_mismatches(self):
        topology_rows, candidate_rows, exact_by_point = self._artifact_rows()
        filtered = rt.filter_closed_shape_membership_candidates_by_owner_face(
            candidate_rows,
            topology_rows,
            OWNER_FACE_BY_POINT,
        )
        filtered_by_point = {}
        for row in filtered:
            filtered_by_point.setdefault(int(row["point_id"]), []).append(int(row["shape_id"]))

        self.assertEqual(set(filtered_by_point), set(exact_by_point))
        for point_id, exact_shape_ids in exact_by_point.items():
            self.assertEqual(sorted(filtered_by_point[point_id]), exact_shape_ids)
        self.assertEqual(
            rt.count_closed_shape_membership_candidates_by_owner_face(
                candidate_rows,
                topology_rows,
                OWNER_FACE_BY_POINT,
            ),
            sum(len(values) for values in exact_by_point.values()),
        )

    def test_contract_is_app_agnostic_and_claim_blocked(self):
        contract = rt.validate_owner_face_membership_contract()
        self.assertEqual(contract["contract"], rt.OWNER_FACE_MEMBERSHIP_CONTRACT)
        self.assertTrue(contract["app_agnostic"])
        self.assertFalse(contract["native_engine_may_infer_app_ownership"])
        self.assertTrue(all(value is False for value in contract["claim_boundary"].values()))

    def test_missing_owner_policy_is_fail_closed_by_default(self):
        topology_rows, candidate_rows, _ = self._artifact_rows()
        with self.assertRaises(KeyError):
            rt.filter_closed_shape_membership_candidates_by_owner_face(
                candidate_rows,
                topology_rows,
                {522: 248},
            )
        self.assertTrue(
            rt.filter_closed_shape_membership_candidates_by_owner_face(
                candidate_rows,
                topology_rows,
                {522: 248},
                missing_owner_policy="drop",
            )
        )

    def test_report_keeps_engine_and_app_ownership_split_clear(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RTDL does not infer CDB, GIS, RayJoin, or benchmark semantics", text)
        self.assertIn("app or dataset loader supplies the ownership column", text)
        self.assertIn("No RayJoin-specific terms are required by the contract", text)


if __name__ == "__main__":
    unittest.main()
