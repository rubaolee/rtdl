from __future__ import annotations

import importlib
import json
import struct
import tempfile
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4500_v3_0_m104_rtnn_kitti_same_input_rtdl_gate_2026-06-17.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
README = ROOT / "examples/current/research_benchmarks/rtnn/README.md"
SCRIPT = ROOT / "scripts/goal4500_m104_rtnn_kitti_same_input_rtdl_gate.py"


class Goal4500V30M104RtnnKittiSameInputRtdlGateTest(unittest.TestCase):
    def _write_frame(self, path: Path, rows: tuple[tuple[float, float, float], ...]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            for x, y, z in rows:
                handle.write(struct.pack("<ffff", x, y, z, 1.0))

    def _make_kitti_source(self, root: Path) -> None:
        frame_dir = root / "2011_09_26" / "2011_09_26_drive_0001_sync" / "velodyne_points" / "data"
        self._write_frame(frame_dir / "0000000000.bin", ((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)))
        self._write_frame(frame_dir / "0000000001.bin", ((7.0, 8.0, 9.0), (10.0, 11.0, 12.0)))

    def test_recipe_csv_export_preserves_recipe_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._make_kitti_source(root)
            export = rt.write_kitti_paper_family_recipe_csv(
                Path(tmpdir) / "points.csv",
                target_handle="kitti_1m",
                source_root=root,
                target_point_count=3,
            )
            lines = Path(export.path).read_text(encoding="utf-8").splitlines()
            self.assertEqual(3, export.point_count)
            self.assertEqual(["1,2,3", "4,5,6", "7,8,9"], lines)
            self.assertEqual("rtnn_csv_xyz", export.format)
            self.assertEqual("bounded_family_recipe_not_exact_paper_recipe", export.paper_equivalence_status)

    def test_script_build_packet_can_stop_after_csv_export(self) -> None:
        module = importlib.import_module("scripts.goal4500_m104_rtnn_kitti_same_input_rtdl_gate")
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "source"
            self._make_kitti_source(root)
            packet = module.build_packet(
                source_root=root,
                work_dir=Path(tmpdir) / "work",
                target_point_count=4,
                run_live=False,
            )
        self.assertEqual("rtdl.v3_0.rtnn_kitti_same_input_rtdl_gate.goal4500.v1", packet["version"])
        self.assertTrue(packet["summary"]["csv_export_ready"])
        self.assertFalse(packet["summary"]["live_rtdl_pair_ready"])
        self.assertEqual(4, packet["input"]["csv_export"]["point_count"])
        self.assertFalse(packet["claim_boundary"]["author_rtnn_comparison"])
        self.assertFalse(packet["claim_boundary"]["paper_reproduction_wording_allowed"])

    def test_packet_docs_and_current_guidance_are_refreshed(self) -> None:
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

        self.assertEqual("rtdl.v3_0.rtnn_kitti_same_input_rtdl_gate.goal4500.v1", packet["version"])
        self.assertEqual("Goal4500 / V3 M104", packet["goal"])
        self.assertTrue(packet["summary"]["csv_export_ready"])
        self.assertTrue(packet["summary"]["live_rtdl_pair_ready"])
        self.assertTrue(packet["summary"]["tie_stable_signature_match"])
        self.assertFalse(packet["summary"]["strict_signature_match"])
        self.assertGreater(packet["summary"]["optix_over_embree_speedup"], 1.0)
        self.assertFalse(packet["claim_boundary"]["author_rtnn_comparison"])
        self.assertFalse(packet["claim_boundary"]["paper_reproduction_wording_allowed"])
        self.assertTrue(packet["claim_boundary"]["tie_sensitive_kth_mismatch"])
        self.assertIn("Goal4500 / V3 M104", report)
        self.assertIn("tie-sensitive kth-id checksum", report)
        self.assertIn("Goal4500 RTNN KITTI same-input RTDL gate", index)
        self.assertIn("same bounded KITTI CSV", readme)
        self.assertIn("run_live", script)
        self.assertEqual("rtdl.v3_0.current_benchmark_route_decisions.goal4503.v1", route["version"])
        self.assertEqual("rtdl.v3_0.current_benchmark_adequacy.goal4503.v1", adequacy["version"])
        self.assertIn("Goal4500", route["evidence_refs"])
        self.assertIn("Goal4500", adequacy["evidence_refs"])
        self.assertIn("fused RTNN-style", route["next_runtime_action"])
        self.assertIn("fused RTNN-style", adequacy["next_generic_runtime_action"])


if __name__ == "__main__":
    unittest.main()
