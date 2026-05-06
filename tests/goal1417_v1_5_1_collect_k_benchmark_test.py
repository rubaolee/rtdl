from __future__ import annotations

import unittest

import rtdsl as rt
from scripts import goal1417_v1_5_1_collect_k_benchmark as bench


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


class Goal1417V151CollectKBenchmarkTest(unittest.TestCase):
    def test_benchmark_accepts_matching_fake_backend(self) -> None:
        report = bench.run_benchmark_package(
            copies=(1, 2),
            backends=("embree",),
            required_backends=("embree",),
            repeats=2,
            warmups=0,
            backend_runners={"embree": _fake_backend_runner},
        )

        self.assertTrue(report["accepted"])
        self.assertEqual(report["backend_summary"]["embree"]["pass"], 2)
        self.assertEqual(report["scale_results"][0]["candidate_count"], 2)
        self.assertEqual(report["scale_results"][1]["candidate_count"], 4)

    def test_benchmark_rejects_required_backend_skip(self) -> None:
        def unavailable(_left, _right, _capacity):
            raise OSError("test backend library missing")

        report = bench.run_benchmark_package(
            copies=(1,),
            backends=("optix",),
            required_backends=("optix",),
            repeats=1,
            warmups=0,
            backend_runners={"optix": unavailable},
        )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["backend_summary"]["optix"]["skipped"], 1)
        self.assertEqual(report["skipped_required"], ["copies=1 backend=optix"])

    def test_benchmark_rejects_row_mismatch(self) -> None:
        def wrong_rows(_left, _right, capacity):
            return rt.collect_k_bounded_rows(((999, 999),), k=capacity, row_width=2) | {
                "backend": "embree",
                "complete_candidate_coverage": True,
            }

        report = bench.run_benchmark_package(
            copies=(1,),
            backends=("embree",),
            repeats=1,
            warmups=0,
            backend_runners={"embree": wrong_rows},
        )

        self.assertFalse(report["accepted"])
        self.assertEqual(report["backend_summary"]["embree"]["fail"], 1)

    def test_markdown_keeps_no_claim_boundary(self) -> None:
        report = bench.run_benchmark_package(
            copies=(1,),
            backends=("embree",),
            repeats=1,
            warmups=0,
            backend_runners={"embree": _fake_backend_runner},
        )

        rendered = bench.render_markdown(report)

        self.assertIn("not a speedup claim", rendered)
        self.assertIn("## Timing Table", rendered)
        self.assertIn("backend=embree status=pass", rendered)


if __name__ == "__main__":
    unittest.main()
