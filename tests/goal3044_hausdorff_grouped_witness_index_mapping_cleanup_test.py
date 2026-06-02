from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal3044_hausdorff_grouped_witness_index_mapping_cleanup_2026-06-02.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal3044_grouped_reduced_witness_index_smoke_a4000_2026-06-02.json"
APP = (
    REPO_ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "hausdorff_xhd"
    / "rtdl_hausdorff_v2_function.py"
)


class Goal3044HausdorffGroupedWitnessIndexMappingCleanupTest(unittest.TestCase):
    def test_report_documents_review_response_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal3044",
            "Goal3043 Claude review",
            "sorted_target_columns",
            "target index in BVH-sort order",
            "_directed_rt_grouped_reduced_nearest_witness",
            "_directed_rt_grouped_adaptive_reduced_nearest_witness",
            "_directed_rt_grouped_device_columns_numba_argmax_nearest_witness",
            "does not alter native ABI",
            "A4000 pod smoke passed",
            "target index `58`",
        ):
            self.assertIn(phrase, text)

    def test_pod_smoke_matches_openmp_witness_identity(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        openmp = data["results"]["openmp_cpu"]
        grouped = data["results"]["rtdl_rt_grouped_reduced_nearest_witness"]

        self.assertTrue(openmp["ok"])
        self.assertTrue(grouped["ok"])
        self.assertTrue(grouped["matches_exact_reference"])
        for field in ("distance", "direction", "source_index", "target_index"):
            self.assertEqual(grouped[field], openmp[field])

    def test_grouped_one_row_reducers_use_original_target_columns(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertNotIn("_reduce_nearest_max_distance_row(source_columns, sorted_target_columns", source)
        for function_name in (
            "_directed_rt_grouped_reduced_nearest_witness",
            "_directed_rt_grouped_active_frontier_nearest_witness",
            "_directed_rt_grouped_adaptive_reduced_nearest_witness",
            "_directed_rt_grouped_device_columns_numba_argmax_nearest_witness",
        ):
            start = source.index(f"def {function_name}")
            end = source.find("\ndef ", start + 1)
            body = source[start:] if end == -1 else source[start:end]
            self.assertIn("_reduce_nearest_max_distance_row(source_columns, target_columns", body)

    def test_v2_6_roadmap_indexes_cleanup_without_claims(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(repo_root=REPO_ROOT)

        self.assertEqual(roadmap["hausdorff_witness_index_cleanup_goal"], "Goal3044")
        self.assertIn("original_target_columns", roadmap["hausdorff_witness_index_cleanup_status"])
        self.assertIn("a4000_smoke_passed", roadmap["hausdorff_witness_index_cleanup_status"])
        self.assertIn("not_native_or_speedup_work", roadmap["hausdorff_witness_index_cleanup_status"])
        self.assertEqual(
            roadmap["hausdorff_witness_index_cleanup_artifact"],
            "docs/reports/goal3044_grouped_reduced_witness_index_smoke_a4000_2026-06-02.json",
        )
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["public_speedup_claim_authorized"])
        self.assertEqual("accept", validation["status"])


if __name__ == "__main__":
    unittest.main()
