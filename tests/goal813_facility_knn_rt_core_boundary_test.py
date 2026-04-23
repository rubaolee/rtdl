import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

import rtdsl as rt
from examples import rtdl_facility_knn_assignment as facility_app


class Goal813FacilityKnnRtCoreBoundaryTest(unittest.TestCase):
    def test_facility_knn_is_not_promoted_to_optix_or_rtx_claim(self) -> None:
        self.assertEqual(
            rt.app_engine_support("facility_knn_assignment", "optix").status,
            "not_exposed_by_app_cli",
        )
        self.assertEqual(
            rt.optix_app_performance_support("facility_knn_assignment").performance_class,
            "not_optix_exposed",
        )
        self.assertEqual(
            rt.optix_app_benchmark_readiness("facility_knn_assignment").status,
            "exclude_from_rtx_app_benchmark",
        )
        self.assertEqual(
            rt.rt_core_app_maturity("facility_knn_assignment").current_status,
            "needs_optix_app_surface",
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
            "knn ranking",
            "nearest-neighbor ordering",
            "fixed-radius",
            "cuda-through-optix",
            "local correctness gate",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, notes)

    def test_public_cli_still_rejects_optix_backend(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            facility_app.main(["--backend", "optix"])
        self.assertIn("invalid choice", stderr.getvalue())

    def test_runtime_helper_still_rejects_optix_backend(self) -> None:
        case = facility_app.make_facility_knn_case()
        with self.assertRaisesRegex(ValueError, "unsupported backend `optix`"):
            facility_app._run_rows("optix", case)

    def test_doc_records_no_fixed_radius_substitution(self) -> None:
        text = (
            Path(__file__).resolve().parents[1] / "docs" / "app_engine_support_matrix.md"
        ).read_text(encoding="utf-8")
        for phrase in (
            "fixed-radius threshold traversal cannot emit ranked nearest-depot assignments",
            "real RT traversal plus ranking design",
            "native traversal/ranking design exists",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
