from __future__ import annotations

import unittest

import rtdsl as rt
from scripts import goal1416_v1_5_1_collect_k_native_parity as parity


def _fake_backend_runner(left, right, capacity):
    rows = tuple(
        sorted(
            (
                int(row["left_polygon_id"]),
                int(row["right_polygon_id"]),
            )
            for row in rt.polygon_pair_overlap_area_rows_cpu(left, right)
        )
    )
    result = rt.collect_k_bounded_rows(rows, k=capacity, row_width=2) | {
        "backend": "embree",
        "complete_candidate_coverage": True,
    }
    return rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")


class Goal1416V151CollectKNativeParityTest(unittest.TestCase):
    def test_reference_cases_cover_empty_exact_fit_and_fail_closed_overflow(self) -> None:
        cases = {case.name: case for case in parity.build_parity_cases()}

        empty = parity.run_reference_case(cases["empty_zero_capacity"])
        exact = parity.run_reference_case(cases["exact_fit_two_rows"])
        overflow = parity.run_reference_case(cases["one_short_fail_closed_overflow"])

        self.assertEqual(empty["status"], "pass")
        self.assertEqual(empty["expected_rows"], ())
        self.assertEqual(exact["status"], "pass")
        self.assertEqual(exact["expected_rows"], ((1, 10), (2, 11)))
        self.assertEqual(overflow["status"], "pass")
        self.assertTrue(overflow["observed_overflow"])

    def test_acceptance_package_accepts_matching_backend_and_overflow_semantics(self) -> None:
        report = parity.run_acceptance_package(
            backends=("embree",),
            required_backends=("embree",),
            backend_runners={"embree": _fake_backend_runner},
        )

        self.assertTrue(report["accepted"])
        self.assertEqual(report["backend_summary"]["embree"]["pass"], 4)
        self.assertEqual(report["backend_summary"]["embree"]["fail"], 0)
        self.assertEqual(report["backend_summary"]["embree"]["skipped"], 0)

    def test_acceptance_package_rejects_required_backend_skip(self) -> None:
        def unavailable(_left, _right, _capacity):
            raise OSError("test backend library missing")

        report = parity.run_acceptance_package(
            backends=("embree",),
            required_backends=("embree",),
            backend_runners={"embree": unavailable},
        )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["backend_summary"]["embree"]["skipped"], 4)
        self.assertEqual(len(report["skipped_required"]), 4)

    def test_markdown_records_verdict_and_paths(self) -> None:
        report = parity.run_acceptance_package(
            backends=("embree",),
            backend_runners={"embree": _fake_backend_runner},
        )

        rendered = parity.render_markdown(report)

        self.assertIn("## Verdict", rendered)
        self.assertIn("## Run Scope", rendered)
        self.assertIn("## Parity Outcome", rendered)
        self.assertIn("docs/reports/goal1416_v1_5_1_collect_k_native_parity_2026-05-06.json", rendered)


if __name__ == "__main__":
    unittest.main()
