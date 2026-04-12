import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal266V05RtnnBaselineRegistryTest(unittest.TestCase):
    def test_rtnn_baseline_registry_covers_paper_set(self) -> None:
        libraries = rt.rtnn_baseline_libraries()
        labels = {library.paper_label for library in libraries}
        self.assertTrue({"cuNSearch", "FRNN", "PCLOctree", "FastRNN"}.issubset(labels))

    def test_repo_existing_baselines_are_labeled_nonpaper_or_bounded(self) -> None:
        scipy = rt.rtnn_baseline_libraries(handle="scipy_ckdtree")
        postgis = rt.rtnn_baseline_libraries(handle="postgis")
        self.assertEqual(scipy[0].current_status, "online_2d_only")
        self.assertEqual(postgis[0].current_status, "online_2d_only")
        self.assertIn("not part of the RTNN paper comparison set", postgis[0].notes)

    def test_prioritized_first_adapter_is_cunsearch(self) -> None:
        decisions = rt.rtnn_baseline_decisions(verdict="prioritize_first_adapter")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].library_handle, "cunsearch")

    def test_pcl_octree_is_explicitly_marked_high_friction(self) -> None:
        decisions = rt.rtnn_baseline_decisions(library_handle="pcl_octree")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].verdict, "defer_until_packaging_plan")

    def test_all_paper_set_libraries_are_3d_targets(self) -> None:
        handles = {"cunsearch", "frnn", "pcl_octree", "fastrnn"}
        libs = [library for library in rt.rtnn_baseline_libraries() if library.handle in handles]
        self.assertEqual({library.target_dimension for library in libs}, {"3d"})


if __name__ == "__main__":
    unittest.main()
