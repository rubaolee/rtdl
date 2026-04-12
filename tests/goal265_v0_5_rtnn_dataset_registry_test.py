import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class Goal265V05RtnnDatasetRegistryTest(unittest.TestCase):
    def test_rtnn_dataset_families_cover_expected_three_families(self) -> None:
        families = rt.rtnn_dataset_families()
        self.assertEqual(len(families), 3)
        self.assertEqual(
            {family.handle for family in families},
            {
                "kitti_velodyne_point_sets",
                "stanford_3d_scan_point_sets",
                "nbody_or_millennium_snapshots",
            },
        )

    def test_all_rtnn_dataset_families_are_3d(self) -> None:
        families = rt.rtnn_dataset_families()
        self.assertEqual({family.dimensionality for family in families}, {"3d"})

    def test_dataset_handle_filter_returns_one_family(self) -> None:
        family = rt.rtnn_dataset_families(handle="kitti_velodyne_point_sets")
        self.assertEqual(len(family), 1)
        self.assertEqual(family[0].paper_label, "KITTI-derived point sets")

    def test_rtnn_targets_preserve_bounded_vs_exact_vs_extension_labels(self) -> None:
        tiers = {target.reproduction_tier for target in rt.rtnn_experiment_targets()}
        self.assertEqual(
            tiers,
            {"bounded_reproduction", "exact_reproduction_candidate", "rtdl_extension"},
        )

    def test_bounded_targets_reference_new_bounded_knn_rows_surface(self) -> None:
        bounded = rt.rtnn_experiment_targets(reproduction_tier="bounded_reproduction")
        self.assertTrue(bounded)
        self.assertTrue(all("bounded_knn_rows" in target.workload.split("|") for target in bounded))

    def test_rtnn_local_profiles_exist_for_each_family(self) -> None:
        profiles = rt.rtnn_local_profiles(artifact="dataset_packaging")
        self.assertEqual(len(profiles), 3)
        self.assertTrue(all(profile.target_runtime == "<=10 minutes total package" for profile in profiles))


if __name__ == "__main__":
    unittest.main()
