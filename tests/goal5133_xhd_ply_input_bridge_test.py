from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from run_xhd_author_json_gate import build_summary as build_author_summary
from run_xhd_rtdl_route_gate import build_summary as build_rtdl_summary
from xhd_input_loader import load_ascii_ply_vertices
from xhd_input_loader import translate_points_to_min_bound


def _write_ascii_ply(path: Path, points: list[tuple[float, float, float]]) -> None:
    rows = [
        "ply",
        "format ascii 1.0",
        f"element vertex {len(points)}",
        "property float x",
        "property float y",
        "property float z",
        "element face 0",
        "property list uchar int vertex_indices",
        "end_header",
    ]
    rows.extend(f"{x} {y} {z}" for x, y, z in points)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


class Goal5133XhdPlyInputBridgeTest(unittest.TestCase):
    def test_ascii_ply_loader_reads_vertices_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "points.ply"
            _write_ascii_ply(path, [(0.0, 1.0, 2.0), (3.0, 4.0, 5.0)])
            self.assertEqual(
                load_ascii_ply_vertices(path, n_dims=3),
                [(0.0, 1.0, 2.0), (3.0, 4.0, 5.0)],
            )

    def test_author_summary_accepts_ply_without_author_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.ply"
            b = Path(tmp) / "b.ply"
            _write_ascii_ply(a, [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)])
            _write_ascii_ply(b, [(0.0, 0.0, 0.0)])
            summary = build_author_summary(
                argparse.Namespace(
                    input1=str(a),
                    input2=str(b),
                    n_dims=3,
                    input_type="ply",
                    translate_each_input_to_min_bound=False,
                    author_bin=None,
                    author_json=None,
                    execution="gpu",
                    variant="rt",
                    tolerance=1e-9,
                )
            )
            self.assertEqual(summary["input_type"], "ply")
            self.assertEqual(summary["rtdl_reference"]["directed_a_to_b"], 2.0)
            self.assertEqual(summary["author_comparison_reference_value"], 2.0)
            self.assertIsNone(summary["matched"])

    def test_rtdl_route_gate_accepts_small_ply_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.ply"
            b = Path(tmp) / "b.ply"
            _write_ascii_ply(a, [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)])
            _write_ascii_ply(b, [(0.0, 0.0, 0.0)])
            summary = build_rtdl_summary(
                argparse.Namespace(
                    input1=str(a),
                    input2=str(b),
                    n_dims=3,
                    input_type="ply",
                    translate_each_input_to_min_bound=False,
                    author_json=None,
                    summary=str(Path(tmp) / "summary.json"),
                    tolerance=1e-9,
                )
            )
            self.assertEqual(summary["input_type"], "ply")
            self.assertEqual(summary["rtdl_route"]["directed_a_to_b"]["distance"], 2.0)
            self.assertTrue(summary["rtdl_matches_exact_reference"])
            self.assertIsNone(summary["matched"])

    def test_binary_ply_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "binary.ply"
            path.write_text(
                "\n".join(
                    [
                        "ply",
                        "format binary_little_endian 1.0",
                        "element vertex 1",
                        "property float x",
                        "property float y",
                        "property float z",
                        "end_header",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "must be ASCII PLY"):
                load_ascii_ply_vertices(path, n_dims=3)

    def test_translate_each_input_to_min_bound_matches_author_ply_convention(self) -> None:
        points = [(-2.0, 1.0, 5.0), (3.0, 4.0, 7.0)]
        self.assertEqual(translate_points_to_min_bound(points), [(0.0, 0.0, 0.0), (5.0, 3.0, 2.0)])


if __name__ == "__main__":
    unittest.main()
