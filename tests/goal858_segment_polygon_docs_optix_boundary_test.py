from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal858SegmentPolygonDocsOptixBoundaryTest(unittest.TestCase):
    def test_feature_docs_explain_optix_mode_and_rt_core_boundary(self) -> None:
        checks = {
            "docs/features/segment_polygon_hitcount/README.md": (
                "--backend optix --optix-mode native",
                "--require-rt-core",
                "strict RTX validation",
                "host-indexed fallback",
            ),
            "docs/features/segment_polygon_anyhit_rows/README.md": (
                "--output-mode segment_counts --optix-mode native",
                "--output-mode rows --optix-mode native",
                "Goal873 added the strict RTX gate",
                "bounded native OptiX pair-row emitter",
                "--require-rt-core",
            ),
        }
        for relative, phrases in checks.items():
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(relative=relative, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_tutorial_explains_optix_mode_boundary(self) -> None:
        text = (ROOT / "docs/tutorials/segment_polygon_workloads.md").read_text(encoding="utf-8")
        for phrase in (
            "--optix-mode auto",
            "--optix-mode host_indexed",
            "--optix-mode native",
            "not released NVIDIA RT-core claims",
            "Goal873 strict RTX gate",
            "bounded native pair-row emitter",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
