from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from prepare_xhd_ply_sample import build_summary
from prepare_xhd_ply_sample import deterministic_sample
from xhd_input_loader import load_ascii_ply_vertices


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


class Goal5134XhdPlySampleGatePacketTest(unittest.TestCase):
    def test_deterministic_sample_includes_first_and_last(self) -> None:
        points = [(float(i), 0.0, 0.0) for i in range(10)]
        self.assertEqual(deterministic_sample(points, count=4), [points[0], points[3], points[6], points[9]])

    def test_sample_summary_and_output_ply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.ply"
            out = Path(tmp) / "sample.ply"
            summary = Path(tmp) / "summary.json"
            _write_ascii_ply(src, [(float(i), float(i + 1), float(i + 2)) for i in range(10)])
            payload = build_summary(
                argparse.Namespace(
                    input=str(src),
                    output=str(out),
                    summary=str(summary),
                    n_dims=3,
                    count=4,
                )
            )
            self.assertEqual(payload["input_point_count"], 10)
            self.assertEqual(payload["sample_point_count"], 4)
            self.assertFalse(payload["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
            self.assertEqual(load_ascii_ply_vertices(out, n_dims=3), [(0.0, 1.0, 2.0), (3.0, 4.0, 5.0), (6.0, 7.0, 8.0), (9.0, 10.0, 11.0)])


if __name__ == "__main__":
    unittest.main()
