from __future__ import annotations

import unittest

import rtdsl as rt


class Goal1413V151CollectKResultValidatorTest(unittest.TestCase):
    def test_validator_accepts_complete_generic_result(self) -> None:
        result = rt.collect_k_bounded_rows(((2, 20), (1, 10)), k=2, row_width=2) | {
            "backend": "embree",
        }

        validated = rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

        self.assertTrue(validated["app_generic"])
        self.assertEqual(validated["candidate_id_rows"], ((1, 10), (2, 20)))
        self.assertEqual(validated["valid_count"], 2)
        self.assertEqual(validated["generic_result_layout"], "dense_candidate_id_rows_with_valid_count")

    def test_validator_rejects_backend_mismatch(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2) | {
            "backend": "embree",
        }

        with self.assertRaisesRegex(ValueError, "backend does not match"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="optix")

    def test_validator_rejects_overflow_metadata(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2) | {
            "backend": "embree",
            "overflowed": True,
        }

        with self.assertRaisesRegex(RuntimeError, "reported overflow"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

    def test_validator_rejects_incomplete_coverage(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2) | {
            "backend": "embree",
            "complete_candidate_coverage": False,
        }

        with self.assertRaisesRegex(RuntimeError, "complete candidate coverage"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

    def test_validator_rejects_width_mismatch(self) -> None:
        result = rt.collect_k_bounded_rows((1, 2), k=2, row_width=1) | {
            "backend": "embree",
        }

        with self.assertRaisesRegex(ValueError, "candidate row width mismatch"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

    def test_validator_rejects_noncanonical_rows(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10), (2, 20)), k=2, row_width=2) | {
            "backend": "embree",
            "candidate_id_rows": ((2, 20), (1, 10)),
        }

        with self.assertRaisesRegex(ValueError, "candidate_id_rows must be canonicalized"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

    def test_validator_rejects_missing_capacity_and_valid_count_metadata(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2) | {
            "backend": "embree",
        }
        result.pop("capacity")
        result.pop("valid_count")

        with self.assertRaisesRegex(ValueError, "capacity or valid_count metadata"):
            rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

    def test_validator_accepts_valid_count_without_capacity_for_transition_results(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10),), k=1, row_width=2) | {
            "backend": "embree",
        }
        result.pop("capacity")

        validated = rt.validate_collect_k_bounded_result(result, row_width=2, backend="embree")

        self.assertEqual(validated["capacity"], 1)
        self.assertEqual(validated["valid_count"], 1)

    def test_jaccard_bridge_uses_validator_for_candidate_id_rows(self) -> None:
        result = rt.collect_k_bounded_rows(((1, 10), (2, 20)), k=2, row_width=2) | {
            "backend": "embree",
            "valid_count": 1,
        }

        with self.assertRaisesRegex(ValueError, "valid_count metadata mismatch"):
            rt.run_generic_polygon_set_jaccard_score_reduction(
                left=(),
                right=(),
                collection=result,
                backend="embree",
                exact_score_fn=lambda *_args: (),
            )


if __name__ == "__main__":
    unittest.main()
