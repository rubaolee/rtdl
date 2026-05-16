import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "goal2126_public_hausdorff_dataset_perf.py"


class Goal2138PublicGeoHarnessTest(unittest.TestCase):
    def test_public_geo_suite_is_explicit_and_bounded(self) -> None:
        text = HARNESS.read_text(encoding="utf-8")
        self.assertIn('"public-geo"', text)
        self.assertIn("PUBLIC_GEO_DATASETS", text)
        self.assertIn("tl_2023_us_county.zip", text)
        self.assertIn("tl_2023_us_zcta520.zip", text)
        self.assertIn("ne_10m_lakes.zip", text)
        self.assertIn("ne_10m_parks_and_protected_lands.zip", text)
        self.assertIn('"xhd_original_wkt_files": False', text)
        self.assertIn('"xhd_paper_exact_dataset_evidence": False', text)

    def test_public_geo_loader_uses_streaming_reservoir_sampling(self) -> None:
        text = HARNESS.read_text(encoding="utf-8")
        self.assertIn("def _load_shapefile_xy_sample", text)
        self.assertIn("reservoir = np.empty((sample_count, 2)", text)
        self.assertIn("replacement = int(rng.integers(total_points))", text)
        self.assertIn("shapefile sample progress", text)


if __name__ == "__main__":
    unittest.main()
