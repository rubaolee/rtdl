import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2134_xhd_graphics_dataset_perf_2026-05-16.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2134_xhd_graphics_pod_a5000"


class Goal2134XhdGraphicsDatasetPerfTest(unittest.TestCase):
    def test_xhd_graphics_artifacts_match_and_show_speedup(self) -> None:
        artifacts = sorted(ARTIFACT_DIR.glob("xhd_graphics_xy_*_group_*.json"))
        self.assertEqual(len(artifacts), 6)
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

        cases = {row["case"] for row in rows}
        self.assertEqual(
            cases,
            {
                "xhd_graphics_dragon_vs_asian_dragon_xy",
                "xhd_graphics_thai_statuette_vs_happy_buddha_xy",
                "xhd_graphics_dragon_vs_happy_buddha_xy",
                "xhd_graphics_thai_statuette_vs_asian_dragon_xy",
            },
        )
        self.assertEqual(len(rows), 24)
        self.assertLess(max(row["rtdl_seeded_pruned_vs_cupy_grouped_grid_ratio"] for row in rows), 0.26)

        best_by_case = {}
        for row in rows:
            key = (row["sample_count"], row["case"])
            current = best_by_case.setdefault(key, {"cupy": float("inf"), "rtdl": float("inf")})
            current["cupy"] = min(current["cupy"], row["cupy_grouped_grid_rawkernel"]["elapsed_sec"])
            current["rtdl"] = min(current["rtdl"], row["rtdl_rt_grouped_seeded_pruned_nearest_witness"]["elapsed_sec"])
        self.assertLess(max(best["rtdl"] / best["cupy"] for best in best_by_case.values()), 0.25)

    def test_report_records_precise_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Full 3D surface Hausdorff reproduction of the X-HD paper | `not-claimed`", report)
        self.assertIn("MRI or geo WKT X-HD dataset reproduction | `not-claimed`", report)
        self.assertIn("RTDL/OptiX beats grouped CuPy", report)
        self.assertIn("Artifacts are in `docs/reports/goal2134_xhd_graphics_pod_a5000/`.", report)


if __name__ == "__main__":
    unittest.main()
