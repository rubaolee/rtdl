from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.goal5757_lane_probe_framework import LaneClassification, validate_lane_probe
from scripts.goal5757_semantic_coverage import (
    LaneSemanticCoverageError,
    fragment_capabilities,
    require_complete_lane,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history/internal_docs/goal5757_lane_probe_evidence_20260811"


class Goal5757ExecutableLaneCoverageTest(unittest.TestCase):
    def test_matrix_is_nine_apps_thirteen_lanes_and_honestly_unfavorable(self):
        matrix = json.loads((EVIDENCE / "MATRIX.json").read_text(encoding="utf-8"))
        self.assertEqual(matrix["paper_app_count"], 9)
        self.assertEqual(matrix["lane_count"], 13)
        self.assertEqual(matrix["classification_counts"], {
            "SUPPORTED_NOW": 1,
            "PARTNER_ONLY_GAP": 0,
            "MISSING_GENERIC_SEMANTIC": 12,
        })
        self.assertTrue(all(value is False for value in matrix["claim_boundary"].values()))

    def test_every_result_is_closed_shape_and_manifest_bound(self):
        matrix = json.loads((EVIDENCE / "MATRIX.json").read_text(encoding="utf-8"))
        for row in matrix["results"]:
            path = EVIDENCE / row["result_file"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["result_sha256"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(validate_lane_probe(payload).value, row["classification"])

    def test_only_particle_tracking_is_supported_and_goal5753_is_not_relabelled(self):
        matrix = json.loads((EVIDENCE / "MATRIX.json").read_text(encoding="utf-8"))
        supported = [row for row in matrix["results"] if row["classification"] == LaneClassification.SUPPORTED_NOW.value]
        self.assertEqual([(row["app_id"], row["lane_id"]) for row in supported], [
            ("particle_tracking", "tetrahedral_face_point_location_and_boundary_detection")
        ])
        self.assertFalse(matrix["claim_boundary"]["goal5753_relabelled"])
        roster = json.loads((ROOT / "history/internal_docs/goal5757_roster_gate_amendment_a1_particle_tracking_known_regression_20260811.json").read_text(encoding="utf-8"))
        self.assertIn("KNOWN_REGRESSION", roster["ninth_app"]["qualification"])
        self.assertIn("FAILED", roster["ninth_app"]["historical_goal5753_exam_status"])
        self.assertFalse(roster["claim_boundary"]["goal5753_held_out_pass_claimed"])

    def test_independent_verifier_passes(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/goal5757_verify_lane_probe_evidence.py")],
            cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["status"], "PASS")

    def test_fragment_plan_cannot_be_promoted_to_full_lane_plan(self):
        observed = fragment_capabilities(geometry_family="custom_aabb", has_any_hit=True)
        for lane, code in (
            ("point_selection.spatial_bounded.v1", "canonical_plan_missing_bounded_multi_round_topk"),
            ("nearest_state.cell_mbr_exact_witness.v1", "canonical_plan_missing_global_argmax_witness"),
            ("fixed_radius.prepared_spatial_components.v1", "canonical_plan_missing_radius_graph_components"),
        ):
            with self.assertRaises(LaneSemanticCoverageError) as caught:
                require_complete_lane(lane, observed)
            self.assertEqual(caught.exception.code, code)

    def test_no_product_or_paper_app_file_is_part_of_this_tranche(self):
        manifest = json.loads((EVIDENCE / "MANIFEST.json").read_text(encoding="utf-8"))
        for item in manifest["payloads"]:
            self.assertNotIn("src/rtdsl", item["path"])
            self.assertNotIn("Paper-reproduction-apps", item["path"])


if __name__ == "__main__":
    unittest.main()
