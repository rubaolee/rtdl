from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
SCRIPT = ROOT / "scripts/goal4498_m102_rtnn_paper_dataset_targets.py"


class Goal4498V30M102RtnnPaperDatasetTargetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))
        cls.rows = {row["handle"]: row for row in cls.packet["rows"]}

    def test_registry_exposes_all_paper_dataset_targets(self) -> None:
        targets = rt.rtnn_paper_dataset_targets()
        self.assertEqual(9, len(targets))
        self.assertEqual(
            {
                "kitti_1m",
                "kitti_6m",
                "kitti_12m",
                "kitti_25m",
                "stanford_bunny_360k",
                "stanford_dragon_3_6m",
                "stanford_buddha_4_6m",
                "millennium_nbody_9m",
                "millennium_nbody_10m",
            },
            {target.handle for target in targets},
        )
        self.assertEqual(4, len(rt.rtnn_paper_dataset_targets(family_handle="kitti_velodyne_point_sets")))
        self.assertEqual(3, len(rt.rtnn_paper_dataset_targets(family_handle="stanford_3d_scan_point_sets")))
        self.assertEqual(2, len(rt.rtnn_paper_dataset_targets(family_handle="nbody_or_millennium_snapshots")))
        self.assertEqual(25_000_000, rt.rtnn_paper_dataset_targets(handle="kitti_25m")[0].point_count)

    def test_packet_blocks_paper_reproduction_until_exact_recipes_exist(self) -> None:
        self.assertEqual("rtdl.v3_0.rtnn_paper_dataset_targets.goal4498.v1", self.packet["version"])
        self.assertEqual("Goal4498 / V3 M102", self.packet["goal"])
        self.assertEqual(9, self.packet["summary"]["target_count"])
        self.assertTrue(self.packet["summary"]["all_exact_rows_blocked"])
        self.assertFalse(self.packet["summary"]["paper_reproduction_authorized"])
        self.assertFalse(self.packet["summary"]["synthetic_distribution_substitution_authorized"])
        self.assertFalse(self.packet["claim_boundary"]["same_output_author_rtdl_comparison_ready"])
        self.assertFalse(self.packet["author_repo"]["exact_paper_datasets_bundled"])
        self.assertEqual(["src/samplepc.txt"], self.packet["author_repo"]["bundled_point_files"])
        self.assertTrue(JSONL.exists())

        self.assertEqual("blocked_on_frame_recipe", self.rows["kitti_6m"]["exact_recipe_status"])
        self.assertEqual("blocked_on_scan_to_point_recipe", self.rows["stanford_dragon_3_6m"]["exact_recipe_status"])
        self.assertEqual("blocked_on_snapshot_trace_recipe", self.rows["millennium_nbody_10m"]["exact_recipe_status"])
        self.assertIn("never a paper row", self.rows["millennium_nbody_9m"]["bounded_fallback_policy"])

    def test_docs_and_current_guidance_are_refreshed(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rtnn"]

        self.assertIn("Goal4498 / V3 M102", report)
        self.assertIn("KITTI-25M", report)
        self.assertIn("Goal4498 RTNN paper dataset targets", index)
        self.assertIn("rtnn_paper_dataset_targets()", readme)
        self.assertIn("AUTHOR_REPO_PROBE_COMMIT", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4498.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4498.v1", adequacy["version"])
        self.assertIn("Goal4498", route["evidence_refs"])
        self.assertIn("Goal4498", adequacy["evidence_refs"])
        self.assertIn("Goal4498 paper-target acquisition", route["next_runtime_action"])
        self.assertIn("Goal4498 paper-family", adequacy["next_generic_runtime_action"])
        self.assertTrue(route["pod_needed_next"])
        self.assertTrue(adequacy["pod_needed_next"])


if __name__ == "__main__":
    unittest.main()
