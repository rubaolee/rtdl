import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_facility_knn_assignment as facility_app


class Goal813FacilityKnnRtCoreBoundaryTest(unittest.TestCase):
    def test_facility_coverage_decision_is_promoted_to_optix(self) -> None:
        self.assertEqual(
            rt.app_engine_support("facility_knn_assignment", "optix").status,
            "direct_cli_native",
        )
        self.assertEqual(
            rt.optix_app_performance_support("facility_knn_assignment").performance_class,
            "optix_traversal_prepared_summary",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("facility_knn_assignment").status,
            "ready_for_rtx_claim_review",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("facility_knn_assignment").current_status,
            "rt_core_ready",
        )

    def test_facility_knn_notes_explain_ranking_gap(self) -> None:
        notes = "\n".join(
            (
                rt.app_engine_support("facility_knn_assignment", "optix").note,
                rt.optix_app_performance_support("facility_knn_assignment").note,
                rt.optix_app_benchmark_readiness("facility_knn_assignment").benchmark_contract,
                rt.optix_app_benchmark_readiness("facility_knn_assignment").blocker,
                rt.rt_core_app_maturity("facility_knn_assignment").required_action,
                rt.rt_core_app_maturity("facility_knn_assignment").cloud_policy,
            )
        ).lower()
        for phrase in (
            "ranked",
            "knn ranking",
            "fixed-radius",
            "coverage",
            "no ranked knn assignment",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, notes)

    def test_public_cli_accepts_only_explicit_optix_coverage_mode(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "coverage_threshold_prepared"):
            facility_app.run_case("optix")

    def test_runtime_helper_still_rejects_optix_backend(self) -> None:
        case = facility_app.make_facility_knn_case()
        with self.assertRaisesRegex(ValueError, "unsupported backend `optix`"):
            facility_app._run_rows("optix", case)

    def test_doc_records_no_fixed_radius_substitution(self) -> None:
        text = (
            Path(__file__).resolve().parents[1] / "docs" / "app_engine_support_matrix.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "coverage_threshold_prepared",
            "ranked nearest-depot assignment remains outside",
            "no ranked KNN assignment RT-core claim",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
