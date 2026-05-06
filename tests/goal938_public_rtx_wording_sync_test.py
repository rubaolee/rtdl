from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal938PublicRtxWordingSyncTest(unittest.TestCase):
    def test_status_page_names_current_ready_claim_review_paths(self) -> None:
        text = (ROOT / "docs/v1_0_rtx_app_status.md").read_text(encoding="utf-8")
        for phrase in (
            "--backend optix --output-mode compact_summary --require-rt-core",
            "--backend optix --scenario visibility_edges --require-rt-core",
            "--backend optix --optix-summary-mode gap_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode count_summary_prepared --require-rt-core",
            "--backend optix --optix-summary-mode coverage_threshold_prepared --require-rt-core",
            "--backend optix --output-mode summary --optix-mode native --require-rt-core",
            "prepared native segment/polygon hit-count traversal",
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
            "keeps graph plus polygon-pair public speedup wording blocked",
            "graph and polygon-pair public speedup wording stay blocked",
        )
        for phrase in stale_phrases:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

    def test_current_public_docs_name_goal1263_polygon_pair_boundary(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "docs/v1_0_rtx_app_status.md",
                "docs/rtdl_feature_guide.md",
                "docs/release_facing_examples.md",
                "docs/application_catalog.md",
                "docs/app_engine_support_matrix.md",
            )
        )
        for phrase in (
            "Goal1263 promotes bounded polygon-pair wording",
            "RT-assisted LSI/PIP positive candidate discovery",
            "whole-app polygon-overlap speedup remain outside",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        self.assertNotIn(
            "exact area refinement remains CPU/Python-owned; only candidate discovery may enter claim review",
            combined,
        )

    def test_current_public_docs_name_goal1262_jaccard_safe_chunk_boundary(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "docs/v1_0_rtx_app_status.md",
                "docs/v1_0_app_acceleration_inventory.md",
                "docs/app_engine_support_matrix.md",
                "docs/v1_1_optix_status.md",
                "docs/rtdl_feature_guide.md",
            )
        )
        for phrase in (
            "Goal1262 confirms Jaccard correctness at chunk 1024",
            "OptiX remains slower than Embree",
            "no positive public speedup wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)
        self.assertNotIn("larger chunk sizes are diagnostic failures until root-caused", combined)
        self.assertNotIn("larger diagnostic chunk failures", combined)

    def test_polygon_matrix_uses_backend_neutral_v1_5_boundary_wording(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "docs/app_engine_support_matrix.md",
                "docs/v1_0_rtx_app_status.md",
                "docs/v1_1_optix_status.md",
                "docs/rtdl_feature_guide.md",
                "docs/application_catalog.md",
                "docs/release_facing_examples.md",
                "docs/tutorials/segment_polygon_workloads.md",
            )
        )
        for phrase in (
            "backend-neutral native exact-area summary",
            "backend-neutral native set-area/Jaccard summary",
            "native C++ exact area continuation",
            "native C++ exact set-area/Jaccard continuation",
        ):
            with self.subTest(phrase=phrase):
                if phrase.startswith("native C++"):
                    self.assertNotIn(phrase, combined)
                else:
                    self.assertIn(phrase, combined)

    def test_current_public_docs_name_goal1264_db_graph_boundary(self) -> None:
        combined = "\n".join(
            (ROOT / relative).read_text(encoding="utf-8")
            for relative in (
                "docs/v1_0_rtx_app_status.md",
                "docs/v1_0_app_acceleration_inventory.md",
                "docs/app_engine_support_matrix.md",
                "docs/v1_1_optix_status.md",
                "docs/rtdl_feature_guide.md",
            )
        )
        for phrase in (
            "Goal1262/Goal1264 show execution-unblocked but mixed evidence",
            "warm-query median still favors Embree",
            "Goal1267 verifies direct packed-ray OptiX traversal is extremely fast",
            "scene-preparation dominated and mixed versus Embree",
            "Goal1267 verifies the current v1.2 direct packed-ray path",
            "`0.0002s`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)

    def test_v1_1_status_explains_slower_optix_outcome(self) -> None:
        text = (ROOT / "docs" / "v1_1_optix_status.md").read_text(encoding="utf-8")

        for phrase in (
            "Embree is the same-contract CPU RT/BVH baseline",
            "optix_still_slower_with_reason",
            "A slower OptiX result can still be useful v1.1/v1.2 evidence",
            "does not authorize positive public RTX speedup wording",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

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
