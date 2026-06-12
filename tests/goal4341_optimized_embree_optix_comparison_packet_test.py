from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.optimized_optix_embree_comparison_packet import (
    optimized_optix_embree_comparison_packet,
    validate_optimized_optix_embree_comparison_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_optimized_optix_embree_comparison_packet.py"
REPORT = ROOT / "docs" / "reports" / "goal4341_optimized_embree_optix_comparison_packet_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4341_optimized_embree_optix_comparison_packet_2026-06-11.json"
GEMINI_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal4341_gemini_review_goal4339_4340_embree_aabb_optimization_2026-06-11.md"
)
CLAUDE_REVIEW = (
    ROOT
    / "docs"
    / "reviews"
    / "goal4341_claude_review_goal4339_4340_embree_aabb_optimization_2026-06-11.md"
)
CONSENSUS_REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal4341_external_review_consensus_and_optimized_comparison_closeout_2026-06-11.md"
)


class Goal4341OptimizedEmbreeOptixComparisonPacketTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = optimized_optix_embree_comparison_packet()

    def test_validation_accepts_one_measured_pair(self) -> None:
        validation = validate_optimized_optix_embree_comparison_packet()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(1, self.payload["summary"]["measured_pair_count"])
        self.assertEqual(5, self.payload["summary"]["scale_comparison_row_count"])
        self.assertEqual(4, self.payload["summary"]["internal_query_median_ratio_count"])
        self.assertEqual(2, self.payload["summary"]["boundary_limited_phase_ratio_count"])
        self.assertEqual(0, self.payload["summary"]["same_contract_scale_pair_required_count"])
        self.assertEqual(4, self.payload["summary"]["contract_split_pair_required_count"])
        self.assertEqual(10, self.payload["summary"]["app_count"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["release_authorized"])

    def test_librts_pair_uses_optimized_embree_and_same_scale_optix(self) -> None:
        pair = self.payload["measured_pairs"][0]
        self.assertEqual("librts_spatial_index", pair["app"])
        self.assertEqual("generic_prepared_aabb_index_query_2d", pair["contract"])
        self.assertEqual("embree_native_aabb_collision_index", pair["embree_cpu_optimized"]["native_index"])
        self.assertEqual("optix_prepared_aabb_index", pair["optix_rt"]["native_index"])
        self.assertTrue(pair["goal4340_embree_validation"]["small_validated_matches_cpu_reference"])
        self.assertGreater(pair["optimized_embree_query_median_speedup_vs_old_columnar_fallback"], 1000.0)
        self.assertAlmostEqual(pair["optix_query_median_faster_than_optimized_embree"], 18.798465566341978)
        self.assertTrue(pair["query_median_ratio_authorized_for_internal_packet"])
        self.assertFalse(pair["elapsed_total_ratio_authorized"])
        self.assertFalse(pair["public_speedup_claim_authorized"])

    def test_scale_rows_separate_clean_query_ratios_from_boundary_limited_rows(self) -> None:
        rows = {row["app"]: row for row in self.payload["scale_comparison_rows"]}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "triangle_counting",
            },
            set(rows),
        )
        clean = {
            app
            for app, row in rows.items()
            if row["ratio_authorization"] == "internal_query_phase_ratio_only_not_public_claim"
        }
        boundary = {
            app
            for app, row in rows.items()
            if row["ratio_authorization"] == "boundary_limited_traversal_phase_only_no_end_to_end_ratio"
        }
        self.assertEqual({"hausdorff_xhd", "contact_manifold", "triangle_counting"}, clean)
        self.assertEqual({"robot_collision", "raydb_style"}, boundary)
        self.assertEqual("embree", rows["contact_manifold"]["faster_backend_for_metric"])
        self.assertEqual("optix", rows["triangle_counting"]["faster_backend_for_metric"])
        self.assertFalse(rows["robot_collision"]["public_speedup_claim_authorized"])
        self.assertFalse(rows["raydb_style"]["release_authorized"])

    def test_app_table_marks_ratio_and_contract_choice_buckets(self) -> None:
        rows = {row["app"]: row for row in self.payload["planning_rows"]}
        self.assertEqual(set(rows), {
            "hausdorff_xhd",
            "spatial_rayjoin",
            "rt_dbscan",
            "robot_collision",
            "contact_manifold",
            "raydb_style",
            "barnes_hut",
            "librts_spatial_index",
            "rtnn",
            "triangle_counting",
        })
        ratio_rows = [
            row["app"]
            for row in self.payload["planning_rows"]
            if row["query_median_ratio_authorized_for_internal_packet"]
        ]
        self.assertEqual(
            ["hausdorff_xhd", "contact_manifold", "librts_spatial_index", "triangle_counting"],
            ratio_rows,
        )
        boundary_rows = [
            row["app"] for row in self.payload["planning_rows"] if row["boundary_limited_phase_ratio_only"]
        ]
        self.assertEqual(["robot_collision", "raydb_style"], boundary_rows)
        self.assertEqual(rows["librts_spatial_index"]["goal4341_status"], "measured_same_contract_optimized_pair")
        self.assertEqual(rows["rt_dbscan"]["goal4341_status"], "contract_split_pair_required")
        self.assertEqual(rows["rtnn"]["goal4341_status"], "contract_split_pair_required")
        for app, row in rows.items():
            self.assertIn("next_action", row)
            self.assertNotEqual("", row["next_action"])
            self.assertFalse(row["public_speedup_claim_authorized"], app)
            self.assertFalse(row["release_authorized"], app)

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "packet.json"
            out_md = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4341", report)
            self.assertIn("not public speedup authorization", report)
            self.assertIn("librts_spatial_index", report)
            self.assertIn("Scale Rows", report)
            self.assertIn("boundary_limited", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Optimized Embree vs OptiX", text)
        self.assertIn("measured_same_contract_optimized_pair", text)
        self.assertIn("internal_query_ratio_candidate_ready", text)
        self.assertIn("same_scale_boundary_limited", text)
        self.assertIn("contract_split_pair_required", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])

    def test_external_reviews_and_consensus_record_boundaries(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS_REPORT.read_text(encoding="utf-8")

        self.assertIn("`accept`", gemini)
        self.assertIn("accept-with-boundary", claude.lower())
        self.assertIn("Embree 3 availability quirk", consensus)
        self.assertIn("embree_aabb_index_2d_available()", consensus)
        self.assertIn("not public speedup authorization", consensus)
        self.assertIn("Ran 26 tests", consensus)


if __name__ == "__main__":
    unittest.main()
