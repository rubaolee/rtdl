import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2139_public_geo_hausdorff_perf_2026-05-16.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2139_public_geo_pod_a5000"


class Goal2139PublicGeoHausdorffPerfTest(unittest.TestCase):
    def test_public_geo_artifacts_match_and_capture_density_contrast(self) -> None:
        artifacts = sorted(ARTIFACT_DIR.glob("public_geo_xy_*_group_*.json"))
        self.assertEqual(len(artifacts), 4)
        rows = []
        for path in artifacts:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["commit"], "5370a8eeaf3cd8017b8573216e541961a5737468")
            self.assertIn("RTX A5000", payload["gpu"])
            boundary = payload["claim_boundary"]
            self.assertTrue(boundary["public_geo_dataset_family"])
            self.assertFalse(boundary["xhd_original_wkt_files"])
            self.assertFalse(boundary["xhd_paper_exact_dataset_evidence"])
            self.assertTrue(boundary["xy_projection_only"])
            for row in payload["rows"]:
                self.assertTrue(row["matches_cupy_grouped_grid_seeded_pruned"])
                rows.append(row)

        self.assertEqual(len(rows), 8)
        census = [row for row in rows if row["case"] == "public_geo_census_counties_vs_zcta_xy"]
        sparse = [row for row in rows if row["case"] == "public_geo_lakes_vs_parks_xy"]
        self.assertEqual(len(census), 4)
        self.assertEqual(len(sparse), 4)
        self.assertLess(max(row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] for row in census), 0.15)
        self.assertLess(max(row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] for row in sparse), 0.85)
        self.assertGreater(min(row["source_total_points"]["census_zcta"] for row in census), 50_000_000)

    def test_report_keeps_public_geo_boundary_precise(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Original X-HD local WKT files reproduced exactly | `not-claimed`", report)
        self.assertIn("Sparse Natural Earth row is a large RT speedup | `not-claimed`", report)
        self.assertIn("MRI/BraTS X-HD dataset reproduction | `not-claimed`", report)
        self.assertIn("Artifacts are in `docs/reports/goal2139_public_geo_pod_a5000/`.", report)


if __name__ == "__main__":
    unittest.main()
