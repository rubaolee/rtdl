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
            self.assertEqual(set(artifacts.keys()), {"registry", "table3", "table4", "figure15", "sources", "bounded"})
            table3 = Path(artifacts["table3"]).read_text(encoding="utf-8")
            table4 = Path(artifacts["table4"]).read_text(encoding="utf-8")
            figure15 = Path(artifacts["figure15"]).read_text(encoding="utf-8")
            sources = Path(artifacts["sources"]).read_text(encoding="utf-8")
            bounded = Path(artifacts["bounded"]).read_text(encoding="utf-8")
            self.assertIn("County ⊲⊳ Zipcode", table3)
            self.assertIn("overlay-seed analogue", table4)
            self.assertIn("overlay-seed analogue", figure15)
            self.assertIn("datadryad.org", sources)
            self.assertIn("5-10 minutes", bounded)

    def test_public_assets_include_exact_and_derived_source_paths(self) -> None:
        assets = {asset.asset_id: asset for asset in rt.rayjoin_public_assets()}
        self.assertIn("rayjoin_preprocessed_share", assets)
        self.assertIn("lakes_parks_spatialhadoop", assets)
        self.assertEqual(assets["rayjoin_preprocessed_share"].source_type, "dryad-share")

    def test_slice_and_write_cdb_round_trip(self) -> None:
        fixture = Path("tests/fixtures/rayjoin/br_county_subset.cdb")
        dataset = rt.load_cdb(fixture)
        sliced = rt.slice_cdb_dataset(dataset, max_chains=2, name="slice_test")
        self.assertEqual(len(sliced.chains), 2)
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "slice.cdb"
            rt.write_cdb(sliced, out)
            reloaded = rt.load_cdb(out)
            self.assertEqual(reloaded.name, "slice")
            self.assertEqual(len(reloaded.chains), 2)


if __name__ == "__main__":
    unittest.main()
