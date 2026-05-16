import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2143_rtdl_xhd_technical_report_for_external_review_2026-05-16.md"
)


class Goal2143RtdlXhdTechnicalReportTest(unittest.TestCase):
    def test_report_records_design_and_native_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("technical report for external review", text)
        self.assertIn("The native engine must not contain app names or app-specific kernels.", text)
        self.assertIn("rtdl_optix_prepare_point_group_nearest_witness_2d", text)
        self.assertIn("rtdl_optix_write_prepared_point_group_threshold_flags_2d", text)
        self.assertIn("rtdl_optix_reduce_prepared_point_group_nearest_max_distance_2d", text)
        self.assertIn("These names are intentionally not `hausdorff_*`, `xhd_*`, `polygon_*`, or", text)

    def test_report_records_xhd_mapping_and_implementation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for required in (
            "_build_uniform_point_group_columns",
            "_seed_sample_point_columns",
            "_pack_point_columns_for_optix",
            "PreparedOptixPointGroupNearestWitness2D.threshold_flags",
            "hausdorff_distance_2d_rt_grouped_seeded_pruned_nearest_witness",
        ):
            self.assertIn(required, text)
        self.assertIn("X-HD-inspired idea", text)
        self.assertIn("Exact final witness", text)

    def test_report_records_evidence_and_claim_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for numeric in ("6.38x", "9.45x", "13.93x", "12.49x", "1.48x"):
            self.assertIn(numeric, text)
        self.assertIn("52 measured artifact rows", text)
        self.assertIn("Full X-HD paper reproduction | `not-claimed`", text)
        self.assertIn("Full 3D surface Hausdorff | `not-claimed`", text)
        self.assertIn("Universal CUDA-vs-RT speedup | `not-claimed`", text)
        self.assertIn("v2.0 release authorization | `not-authorized-here`", text)

    def test_report_is_ascii_for_external_portability(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        try:
            text.encode("ascii")
        except UnicodeEncodeError as exc:  # pragma: no cover - assertion detail
            self.fail(f"report contains non-ASCII text at offset {exc.start}")


if __name__ == "__main__":
    unittest.main()
