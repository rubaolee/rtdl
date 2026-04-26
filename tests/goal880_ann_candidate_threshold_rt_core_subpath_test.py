from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_ann_candidate_app as app


class _PreparedCandidateThreshold:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query_points, *, radius: float, threshold: int):
        raise AssertionError("ANN candidate RT-core subpath should use scalar count")

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        return len(query_points)


class _PartialPreparedCandidateThreshold(_PreparedCandidateThreshold):
    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        return max(0, len(query_points) - 1)


class Goal880AnnCandidateThresholdRtCoreSubpathTest(unittest.TestCase):
    def test_optix_candidate_threshold_mode_uses_prepared_traversal(self) -> None:
        prepared = _PreparedCandidateThreshold()
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=prepared) as mocked:
            payload = app.run_app(
                "optix",
                optix_summary_mode="candidate_threshold_prepared",
                candidate_radius=0.2,
                require_rt_core=True,
            )

        mocked.assert_called_once()
        self.assertEqual(prepared.query_count, payload["query_count"])
        self.assertEqual(prepared.radius, 0.2)
        self.assertEqual(prepared.threshold, 1)
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["candidate_threshold"]["within_candidate_radius"])
        self.assertEqual(payload["candidate_threshold"]["summary_mode"], "scalar_threshold_count")
        self.assertIsNone(payload["candidate_threshold"]["row_count"])
        self.assertTrue(payload["candidate_threshold"]["identity_parity_available"])
        self.assertTrue(payload["matches_oracle"])
        self.assertIsNone(payload.get("approximate_rows"))
        self.assertIn("candidate-coverage decision", payload["rtdl_role"])
        self.assertIn("not a full ANN index", payload["boundary"])

    def test_optix_candidate_threshold_failure_keeps_scalar_identity_boundary(self) -> None:
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=_PartialPreparedCandidateThreshold()):
            payload = app.run_app(
                "optix",
                optix_summary_mode="candidate_threshold_prepared",
                candidate_radius=0.2,
                require_rt_core=True,
            )

        self.assertFalse(payload["candidate_threshold"]["within_candidate_radius"])
        self.assertIsNone(payload["candidate_threshold"]["uncovered_query_ids"])
        self.assertFalse(payload["candidate_threshold"]["identity_parity_available"])
        self.assertFalse(payload["matches_oracle"])
        self.assertFalse(payload["oracle_decision_matches"])
        self.assertIsNone(payload["oracle_identity_matches"])

    def test_require_rt_core_rejects_default_knn_rows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "candidate_threshold_prepared"):
            app.run_app("optix", require_rt_core=True)

    def test_negative_candidate_radius_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "candidate_radius must be non-negative"):
            app.run_app("optix", optix_summary_mode="candidate_threshold_prepared", candidate_radius=-0.1)

    def test_threshold_rows_missing_queries_are_uncovered(self) -> None:
        case = app.make_ann_case()
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
        )

        summary = app._candidate_threshold_from_count_rows(
            rows,
            query_points=case["query_points"],
            radius=0.2,
        )

        self.assertFalse(summary["within_candidate_radius"])
        self.assertEqual(summary["uncovered_query_ids"], [2, 3])
        self.assertEqual(summary["covered_query_count"], 1)


if __name__ == "__main__":
    unittest.main()
