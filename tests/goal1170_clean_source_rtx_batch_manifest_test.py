import unittest
import tempfile
import json
from pathlib import Path

from scripts.goal1170_clean_source_rtx_batch_intake import build_intake
from scripts.goal1170_clean_source_rtx_batch_manifest import build_manifest, to_runner


class Goal1170CleanSourceRtxBatchManifestTest(unittest.TestCase):
    def test_manifest_covers_six_unreviewed_plus_two_clean_replacements(self):
        payload = build_manifest()

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["summary"]["row_count"], 8)
        self.assertEqual(payload["summary"]["not_reviewed_public_wording_rows"], 6)
        self.assertEqual(payload["summary"]["clean_replacement_rows"], 2)

    def test_skip_validation_is_limited_to_large_timing_replacements(self):
        payload = build_manifest()

        self.assertEqual(
            payload["summary"]["skip_validation_rows"],
            [
                "ann_candidate_large_timing_replacement",
                "robot_pose_count_large_timing_replacement",
            ],
        )

    def test_runner_refuses_dirty_claim_grade_tree(self):
        runner = to_runner(build_manifest())

        self.assertIn("Refusing claim-grade run: git working tree is dirty.", runner)
        self.assertIn("git status --short", runner)
        self.assertIn("nvidia-smi", runner)
        self.assertIn("goal1171_clean_source_rtx_pod_preflight.py", runner)
        self.assertIn("RTDL_OPTIX_LIB", runner)
        self.assertIn("Goal1170 batch complete", runner)

    def test_intake_rejects_missing_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = build_intake(Path(tmp))

        self.assertFalse(payload["valid"])
        self.assertEqual(len(payload["missing_artifacts"]), 8)

    def test_intake_rejects_dirty_source_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            for name in [
                "database_compact_summary.json",
                "graph_visibility_edges.json",
                "road_hazard_native_summary.json",
                "polygon_pair_candidate_discovery.json",
                "polygon_jaccard_safe_chunk.json",
                "hausdorff_threshold_prepared.json",
            ]:
                (path / name).write_text(json.dumps({"source_commit": "abc-local-dirty"}), encoding="utf-8")
            (path / "ann_candidate_65536_timing.json").write_text(
                json.dumps({"source_commit": "abc-local-dirty", "scenario": {"result": {"matches_oracle": None}}}),
                encoding="utf-8",
            )
            (path / "robot_pose_count_262144_timing.json").write_text(
                json.dumps({"source_commit": "abc-local-dirty", "validated": False, "matches_oracle": None}),
                encoding="utf-8",
            )
            payload = build_intake(path)

        self.assertFalse(payload["valid"])
        self.assertEqual(len(payload["dirty_source_artifacts"]), 8)


if __name__ == "__main__":
    unittest.main()
