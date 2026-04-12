import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal267V05RtnnReproductionMatrixTest(unittest.TestCase):
    def test_dataset_packaging_matrix_uses_only_paper_set_libraries(self) -> None:
        entries = rt.rtnn_reproduction_matrix(artifact="dataset_packaging")
        self.assertTrue(entries)
        self.assertNotIn("postgis", {entry.baseline_handle for entry in entries})
        self.assertNotIn("scipy_ckdtree", {entry.baseline_handle for entry in entries})

    def test_comparison_matrix_exposes_nonpaper_rows_honestly(self) -> None:
        entries = rt.rtnn_reproduction_matrix(artifact="comparison_matrix")
        self.assertIn("postgis", {entry.baseline_handle for entry in entries})
        self.assertIn("scipy_ckdtree", {entry.baseline_handle for entry in entries})
        nonpaper = [entry for entry in entries if entry.baseline_handle in {"postgis", "scipy_ckdtree"}]
        self.assertTrue(nonpaper)
        self.assertTrue(all(entry.matrix_status == "nonpaper_comparison_only" for entry in nonpaper))

    def test_exact_reproduction_candidates_are_blocked_honestly(self) -> None:
        entries = rt.rtnn_reproduction_matrix(artifact="paper_matrix")
        exact_entries = [entry for entry in entries if entry.reproduction_tier == "exact_reproduction_candidate"]
        self.assertTrue(exact_entries)
        self.assertTrue(
            all(entry.matrix_status == "blocked_on_exact_dataset_and_adapter" for entry in exact_entries)
        )

    def test_rtdl_extension_entries_are_labeled_as_extensions(self) -> None:
        entries = rt.rtnn_reproduction_matrix(artifact="paper_matrix")
        extension_entries = [entry for entry in entries if entry.reproduction_tier == "rtdl_extension"]
        self.assertTrue(extension_entries)
        self.assertTrue(all(entry.matrix_status == "planned_rtdl_extension" for entry in extension_entries))

    def test_bounded_knn_targets_only_pair_with_supporting_libraries(self) -> None:
        entries = rt.rtnn_reproduction_matrix()
        bounded_entries = [entry for entry in entries if "bounded_knn_rows" in entry.workload.split("|")]
        self.assertTrue(bounded_entries)
        self.assertNotIn("cunsearch", {entry.baseline_handle for entry in bounded_entries})

    def test_fixed_radius_targets_can_pair_with_cunsearch(self) -> None:
        entries = rt.rtnn_reproduction_matrix()
        fixed_radius_entries = [entry for entry in entries if "fixed_radius_neighbors" in entry.workload.split("|")]
        self.assertIn("cunsearch", {entry.baseline_handle for entry in fixed_radius_entries})


if __name__ == "__main__":
    unittest.main()
