import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json"
REPORT = ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.md"


class Goal3328RayJoinCdbTopologyShapeIdProbeTest(unittest.TestCase):
    def test_topology_probe_records_shared_faces_for_all_mismatches(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], "rtdl.goal3328.rayjoin_cdb_topology_shape_id_probe.v1")
        self.assertEqual(data["dataset"], "data/rayjoin_public_cdb/br_county_start256_count512.cdb")
        self.assertEqual(data["topology_row_count"], 512)
        rows = data["per_mismatch_point"]
        self.assertEqual({int(row["point_id"]) for row in rows}, {522, 523, 538, 539, 540, 564, 565})
        self.assertTrue(all(row["shared_face_ids"] for row in rows))

        by_point = {int(row["point_id"]): row for row in rows}
        self.assertEqual(by_point[522]["shared_face_ids"], [247])
        self.assertEqual(by_point[523]["shared_face_ids"], [247])
        self.assertEqual(by_point[538]["shared_face_ids"], [228, 253])
        self.assertEqual(by_point[539]["shared_face_ids"], [228, 253])
        self.assertEqual(by_point[540]["shared_face_ids"], [228, 253])
        self.assertEqual(by_point[564]["shared_face_ids"], [262, 271])
        self.assertEqual(by_point[565]["shared_face_ids"], [262, 271])

    def test_shape_topology_rows_cover_all_examined_shape_ids(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            data["shape_ids_examined"],
            [418, 437, 521, 522, 523, 535, 539, 540, 559, 562, 565],
        )
        topology_rows = data["shape_topology_rows"]
        self.assertEqual(len(topology_rows), len(data["shape_ids_examined"]))
        self.assertTrue(all(row["present"] for row in topology_rows))
        self.assertTrue(all(row["has_left_face"] == 1 and row["has_right_face"] == 1 for row in topology_rows))

    def test_claims_stay_blocked_and_report_states_boundary(self):
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        boundary = data["claim_boundary"]
        self.assertFalse(boundary["release_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])

        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("not an app-specific RayJoin patch inside OptiX", report)
        self.assertIn("generic topology-aware ownership contract", report)
        self.assertIn("must fall back to exact prepared rows", report)


if __name__ == "__main__":
    unittest.main()
