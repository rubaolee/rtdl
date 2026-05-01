from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal938PublicRtxWordingSyncTest(unittest.TestCase):
    def test_front_page_names_current_ready_claim_review_paths(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "--backend optix --output-mode compact_summary --require-rt-core",
            "--backend optix --scenario visibility_edges --require-rt-core",
            "--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode count_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core",
            "--backend optix --output-mode summary --optix-mode native --require-rt-core",
            "prepared native hit-count traversal",
            "prepared bounded native pair-row traversal",
            "polygon pair overlap",
            "polygon set Jaccard",
            "--backend optix --optix-summary-mode directed_threshold_prepared --require-rt-core",
            "--backend optix --optix-summary-mode candidate_threshold_prepared --require-rt-core",
            "--backend optix --optix-summary-mode rt_count_threshold_prepared --output-mode density_count",
            "--backend optix --optix-summary-mode rt_core_flags_prepared --output-mode core_count",
            "--backend optix --optix-summary-mode prepared_count",
            "--backend optix --optix-summary-mode node_coverage_prepared --require-rt-core",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_public_docs_do_not_retain_goal818_rejection_wording(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "README.md",
                "docs/rtdl_feature_guide.md",
                "docs/release_facing_examples.md",
                "docs/application_catalog.md",
                "docs/tutorials/graph_workloads.md",
                "docs/tutorials/segment_polygon_workloads.md",
            )
        )
        stale_phrases = (
            "Rejected under `--require-rt-core` today: graph apps",
            "Graph, facility KNN, polygon overlap/Jaccard",
            "graph, facility KNN, polygon overlap/Jaccard",
            "This app has no OptiX/NVIDIA RT-core surface today",
        )
        for phrase in stale_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

    def test_public_docs_keep_goal941_boundary_wording(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "README.md",
                "docs/rtdl_feature_guide.md",
                "docs/release_facing_examples.md",
                "docs/application_catalog.md",
            )
        )
        for phrase in (
            "not automatic public speedup claims",
            "whole-app speedup",
            "SQL/DBMS behavior",
            "row-materializing DB output",
            "prepared road hazard",
            "Hausdorff exact distance",
            "ANN ranking",
            "Barnes-Hut force reduction",
            "support matrix",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main()
