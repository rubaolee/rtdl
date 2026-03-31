import sys
import unittest

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


class PaperReproductionTest(unittest.TestCase):
    def test_table3_has_all_expected_pairs_for_lsi_and_pip(self) -> None:
        targets = rt.paper_targets(artifact="table3")
        self.assertEqual(len(targets), 16)
        labels = {target.paper_label for target in targets}
        self.assertEqual(
            labels,
            {
                "County ⊲⊳ Zipcode",
                "Block ⊲⊳ Water",
                "LKAF ⊲⊳ PKAF",
                "LKAS ⊲⊳ PKAS",
                "LKAU ⊲⊳ PKAU",
                "LKEU ⊲⊳ PKEU",
                "LKNA ⊲⊳ PKNA",
                "LKSA ⊲⊳ PKSA",
            },
        )

    def test_lakes_parks_suffixes_have_internal_mapping(self) -> None:
        handles = {target.dataset_handle for target in rt.paper_targets(artifact="table3") if target.paper_label.startswith("LK")}
        self.assertEqual(
            handles,
            {
                "lakes_parks_Africa",
                "lakes_parks_Asia",
                "lakes_parks_Australia",
                "lakes_parks_Europe",
                "lakes_parks_North_America",
                "lakes_parks_South_America",
            },
        )

    def test_overlay_targets_exist_for_table4_and_figure15(self) -> None:
        table4 = rt.paper_targets(artifact="table4")
        fig15 = rt.paper_targets(artifact="figure15")
        self.assertEqual(len(table4), 1)
        self.assertEqual(len(fig15), 1)
        self.assertEqual(table4[0].workload, "overlay")
        self.assertEqual(fig15[0].workload, "overlay")


if __name__ == "__main__":
    unittest.main()
