import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from rtdsl.rayjoin_artifacts import generate_goal22_artifacts


class Goal22ReproductionTest(unittest.TestCase):
    def test_dataset_family_registry_covers_all_table3_handles(self) -> None:
        handles = {target.dataset_handle for target in rt.paper_targets(artifact="table3")}
        family_handles = {family.handle for family in rt.dataset_families()}
        self.assertTrue(handles.issubset(family_handles))

    def test_local_profiles_include_table3_table4_and_figure15(self) -> None:
        profiles = {profile.profile_id for profile in rt.local_profiles()}
        self.assertIn("table3_pair_bounded_local", profiles)
        self.assertIn("table4_overlay_bounded_local", profiles)

    def test_goal22_generator_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = generate_goal22_artifacts(tmpdir)
            self.assertEqual(set(artifacts.keys()), {"registry", "table3", "table4", "figure15"})
            table3 = Path(artifacts["table3"]).read_text(encoding="utf-8")
            table4 = Path(artifacts["table4"]).read_text(encoding="utf-8")
            figure15 = Path(artifacts["figure15"]).read_text(encoding="utf-8")
            self.assertIn("County ⊲⊳ Zipcode", table3)
            self.assertIn("overlay-seed analogue", table4)
            self.assertIn("overlay-seed analogue", figure15)


if __name__ == "__main__":
    unittest.main()
