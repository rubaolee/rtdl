import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2136_xhd_graphics_dense_stress_perf_2026-05-16.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2136_xhd_graphics_dense_pod_a5000"


class Goal2136XhdGraphicsDenseStressPerfTest(unittest.TestCase):
    def test_million_point_stress_rows_match_and_remain_fast(self) -> None:
        artifacts = sorted(ARTIFACT_DIR.glob("xhd_graphics_xy_1048576_group_*.json"))
        self.assertEqual(len(artifacts), 2)
        rows = []
        for path in artifacts:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["commit"], "02ee6ab5a7b8e1a78b961772a8eabb27aa1aa052")
            self.assertIn("RTX A5000", payload["gpu"])
            boundary = payload["claim_boundary"]
            self.assertTrue(boundary["xhd_paper_graphics_dataset_names"])
            self.assertFalse(boundary["xhd_paper_exact_dataset_evidence"])
            self.assertTrue(boundary["xy_projection_only"])
            self.assertFalse(boundary["three_dimensional_surface_hausdorff_claim"])
            for row in payload["rows"]:
                self.assertTrue(row["matches_cupy_grouped_grid_seeded_pruned"])
                rows.append(row)

        self.assertEqual(len(rows), 8)
        self.assertLess(max(row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] for row in rows), 0.13)
        dense_rows = [
            row for row in rows
            if row["case"] in {
                "xhd_graphics_thai_statuette_vs_happy_buddha_xy",
                "xhd_graphics_thai_statuette_vs_asian_dragon_xy",
            }
        ]
        self.assertTrue(dense_rows)
        self.assertTrue(all(row["sample_count"] == 1048576 for row in dense_rows))
        self.assertLess(max(row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] for row in dense_rows), 0.09)

    def test_report_keeps_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Full 3D surface Hausdorff reproduction of X-HD | `not-claimed`", report)
        self.assertIn("MRI or geo WKT reproduction | `not-claimed`", report)
        self.assertIn("v2.0 release authorization | `not-authorized-here`", report)
        self.assertIn("Artifacts are in `docs/reports/goal2136_xhd_graphics_dense_pod_a5000/`.", report)


if __name__ == "__main__":
    unittest.main()
