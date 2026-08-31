from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3255_rayjoin_pip_aabb_broadphase_probe_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3255_rayjoin_pip_aabb_broadphase_probe_pod_2026-06-03.json"
SCRIPT = ROOT / "scripts" / "goal3255_rayjoin_pip_aabb_broadphase_probe.py"


class Goal3255RayJoinPipAabbBroadphaseProbePodEvidenceTest(unittest.TestCase):
    def test_report_records_broadphase_diagnostic_without_overclaim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin PIP AABB Broadphase Probe",
            "0.071144 ms",
            "0.780968 ms",
            "1542",
            "1430",
            "It does not mean AABB",
            "can replace exact PIP",
            "AABB point containment is not exact",
            "point-in-polygon or closed-shape membership",
            "device-resident candidate-to-predicate continuation",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_and_bounded(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3255)
        self.assertEqual(data["schema"], "rtdl.goal3255.rayjoin_pip_aabb_broadphase_probe.v1")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["repo_state"]["commit"], "eea2f7b6e1ec676ce6860b5ac0953dba0e254ce0")
        self.assertEqual(data["repo_state"]["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

        self.assertEqual(data["inputs"]["point_count"], 512)
        self.assertEqual(data["inputs"]["shape_count"], 481)
        self.assertEqual(data["inputs"]["aabb_box_count"], 481)

    def test_aabb_is_fast_selective_and_not_exact_authority(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        aabb = data["aabb_point_contains"]
        exact = data["closed_shape_device_filtered"]
        comparison = data["comparison"]

        self.assertEqual(aabb["primitive"], "AABB_INDEX_QUERY_2D")
        self.assertEqual(aabb["operation"], "point_contains")
        self.assertEqual(aabb["candidate_counts"]["samples"], [1542] * 15)
        self.assertEqual(exact["positive_counts"]["samples"], [1430] * 15)

        self.assertAlmostEqual(aabb["timing"]["median_sec"] * 1000.0, 0.0711437314748764)
        self.assertAlmostEqual(exact["timing"]["median_sec"] * 1000.0, 0.7809679955244064)
        self.assertAlmostEqual(comparison["aabb_candidate_to_exact_positive_ratio"], 1.0783216783216782)
        self.assertAlmostEqual(comparison["aabb_time_over_closed_shape_time_ratio"], 0.0910968591319861)

        self.assertFalse(comparison["aabb_broadphase_is_exact_membership"])
        self.assertFalse(comparison["aabb_broadphase_can_replace_closed_shape_count"])
        self.assertIn("candidate-to-predicate continuation", comparison["next_design_implication"])

    def test_script_uses_prepared_generic_query_handles(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("prepare_optix_aabb_index_2d(boxes)", text)
        self.assertIn("prepare_optix_aabb_point_queries_2d(points)", text)
        self.assertIn("count_prepared_queries", text)
        self.assertIn("prepare_point_closed_shape_membership_2d_optix", text)
        self.assertIn("count_device_filtered", text)


if __name__ == "__main__":
    unittest.main()
