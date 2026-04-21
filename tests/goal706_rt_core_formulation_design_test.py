import unittest
from pathlib import Path


class Goal706RtCoreFormulationDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "reports"
            / "goal706_rt_core_formulation_for_current_cuda_through_optix_apps_2026-04-21.md"
        )
        cls.text = cls.report.read_text(encoding="utf-8")

    def test_report_clarifies_excluded_today_is_not_impossible(self):
        for phrase in (
            "not a fundamental statement",
            "Excluded today does not mean impossible",
            "do not benchmark or market the current implementation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_report_maps_each_current_cuda_through_optix_app_to_rt_design(self):
        for phrase in (
            "### Hausdorff Distance",
            "### ANN / KNN Candidate Search",
            "### Barnes-Hut",
            "rt.hausdorff_candidates",
            "rt.knn_candidate_filter",
            "rt.barnes_hut_opening_candidates",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_report_records_paper_specific_technical_mechanisms(self):
        for phrase in (
            "grid grouping",
            "HD estimators",
            "early break",
            "fixed-radius neighbor discovery",
            "filter-refine",
            "monotone transformation",
            "autoropes",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_report_preserves_honesty_boundaries(self):
        for phrase in (
            "RT-assisted candidate generation, not full Hausdorff speedup",
            "RT-assisted candidate filtering only",
            "design feasibility only, not RT-core Barnes-Hut speedup",
            "Python must not own the heavy inner loop",
            "Do not claim RT-core speedup from CUDA-through-OptiX kernels",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
