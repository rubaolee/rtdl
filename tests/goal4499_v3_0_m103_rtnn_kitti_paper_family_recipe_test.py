from __future__ import annotations

import importlib
import json
import os
import struct
import tempfile
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.json"
JSONL = ROOT / "docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.jsonl"
REPORT = ROOT / "docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
SCRIPT = ROOT / "scripts/goal4499_m103_rtnn_kitti_paper_family_recipe.py"


class Goal4499V30M103RtnnKittiPaperFamilyRecipeTest(unittest.TestCase):
    def _write_frame(self, path: Path, point_count: int) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            for index in range(point_count):
                handle.write(struct.pack("<ffff", float(index), 1.0, 2.0, 0.5))

    def _make_kitti_source(self, root: Path) -> None:
        frame_dir = root / "2011_09_26" / "2011_09_26_drive_0001_sync" / "velodyne_points" / "data"
        self._write_frame(frame_dir / "0000000000.bin", 5)
        self._write_frame(frame_dir / "0000000001.bin", 7)
        self._write_frame(frame_dir / "0000000002.bin", 9)

    def test_frame_point_counter_reads_kitti_bin_sizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_kitti_source(root)
            counts = rt.inspect_kitti_frame_point_counts(root)
            self.assertEqual((5, 7, 9), tuple(count.point_count for count in counts))
            self.assertEqual("2011_09_26_drive_0001_sync", counts[0].sequence)

    def test_recipe_planner_reaches_target_and_marks_bounded_not_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_kitti_source(root)
            recipe = rt.plan_kitti_paper_family_recipe(
                target_handle="kitti_1m",
                source_root=root,
                target_point_count=15,
            )
            self.assertEqual("bounded_family_recipe_ready", recipe.recipe_status)
            self.assertEqual(15, recipe.selected_point_count)
            self.assertEqual(3, recipe.selected_frame_count)
            self.assertTrue(recipe.truncated_last_frame)
            self.assertEqual((5, 7, 3), tuple(frame.take_point_count for frame in recipe.frames))
            self.assertEqual("bounded_family_recipe_not_exact_paper_recipe", recipe.paper_equivalence_status)
            self.assertEqual("blocked_on_frame_recipe", recipe.exact_recipe_status)

    def test_recipe_manifest_has_claim_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._make_kitti_source(root)
            manifest = rt.write_kitti_paper_family_recipe_manifest(
                Path(tmpdir) / "recipe.json",
                target_handle="kitti_1m",
                source_root=root,
                target_point_count=12,
            )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual("kitti_paper_family_recipe_manifest_v1", payload["manifest_kind"])
            self.assertTrue(payload["claim_boundary"]["paper_family_dataset"])
            self.assertFalse(payload["claim_boundary"]["exact_paper_recipe"])
            self.assertTrue(payload["claim_boundary"]["same_contract_author_rtdl_bounded_comparison_allowed"])
            self.assertFalse(payload["claim_boundary"]["paper_reproduction_wording_allowed"])

    def test_packet_and_current_guidance_are_refreshed(self) -> None:
        packet = json.loads(PACKET.read_text(encoding="utf-8"))
        report = REPORT.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        route = rt.explain_current_benchmark_route("rtnn")
        adequacy_module = importlib.import_module("rtdsl.current_benchmark_adequacy")
        adequacy = {
            row["app"]: row for row in adequacy_module.current_benchmark_adequacy()
        }["rtnn"]

        self.assertEqual("rtdl.v3_0.rtnn_kitti_paper_family_recipe.goal4499.v1", packet["version"])
        self.assertEqual("Goal4499 / V3 M103", packet["goal"])
        self.assertFalse(packet["claim_boundary"]["paper_reproduction_wording_allowed"])
        self.assertFalse(packet["claim_boundary"]["synthetic_distribution_substitution_authorized"])
        self.assertTrue(JSONL.exists())
        self.assertIn("Goal4499 / V3 M103", report)
        self.assertIn("Goal4499 RTNN KITTI paper-family recipe", index)
        self.assertIn("write_kitti_paper_family_recipe_manifest", readme)
        self.assertIn("DEFAULT_SOURCE_ROOT_CANDIDATES", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4500.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4500.v1", adequacy["version"])
        self.assertIn("Goal4499", route["evidence_refs"])
        self.assertIn("Goal4499", adequacy["evidence_refs"])
        self.assertIn("author RTNN", route["next_runtime_action"])
        self.assertIn("author RTNN", adequacy["next_generic_runtime_action"])
        self.assertTrue(route["pod_needed_next"])
        self.assertTrue(adequacy["pod_needed_next"])

    def test_script_packet_can_use_temporary_source_root(self) -> None:
        module = importlib.import_module("scripts.goal4499_m103_rtnn_kitti_paper_family_recipe")
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source"
            self._make_kitti_source(source)
            old = os.environ.get("RTDL_KITTI_SOURCE_ROOT")
            os.environ["RTDL_KITTI_SOURCE_ROOT"] = str(source)
            try:
                packet = module.build_packet()
            finally:
                if old is None:
                    os.environ.pop("RTDL_KITTI_SOURCE_ROOT", None)
                else:
                    os.environ["RTDL_KITTI_SOURCE_ROOT"] = old
        self.assertTrue(packet["summary"]["source_ready"])
        self.assertEqual(4, packet["summary"]["recipe_row_count"])
        self.assertEqual(0, packet["summary"]["ready_bounded_recipe_count"])
        self.assertFalse(packet["claim_boundary"]["bounded_same_contract_author_rtdl_comparison_allowed"])
        self.assertFalse(packet["summary"]["paper_reproduction_authorized"])


if __name__ == "__main__":
    unittest.main()
