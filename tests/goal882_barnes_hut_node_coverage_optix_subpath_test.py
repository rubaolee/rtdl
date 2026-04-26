from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_barnes_hut_force_app as app


class _PreparedNodeCoverage:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, bodies, *, radius: float, threshold: int):
        raise AssertionError("node coverage app path should not materialize count rows")

    def count_threshold_reached(self, bodies, *, radius: float, threshold: int):
        self.body_count = len(bodies)
        self.radius = radius
        self.threshold = threshold
        return len(bodies)


class _PartialPreparedNodeCoverage(_PreparedNodeCoverage):
    def count_threshold_reached(self, bodies, *, radius: float, threshold: int):
        self.body_count = len(bodies)
        self.radius = radius
        self.threshold = threshold
        return max(0, len(bodies) - 1)


class Goal882BarnesHutNodeCoverageOptixSubpathTest(unittest.TestCase):
    def test_optix_node_coverage_mode_uses_prepared_traversal(self) -> None:
        prepared = _PreparedNodeCoverage()
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=prepared) as mocked:
            payload = app.run_app(
                "optix",
                optix_summary_mode="node_coverage_prepared",
                node_radius=app.NODE_DISCOVERY_RADIUS,
                require_rt_core=True,
            )

        mocked.assert_called_once()
        self.assertEqual(prepared.body_count, payload["body_count"])
        self.assertEqual(prepared.radius, app.NODE_DISCOVERY_RADIUS)
        self.assertEqual(prepared.threshold, 1)
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["node_coverage"]["all_bodies_have_node_candidate"])
        self.assertEqual(payload["node_coverage"]["summary_mode"], "scalar_threshold_count")
        self.assertIsNone(payload["node_coverage"]["row_count"])
        self.assertTrue(payload["node_coverage"]["identity_parity_available"])
        self.assertTrue(payload["matches_oracle"])
        self.assertTrue(payload["oracle_decision_matches"])
        self.assertTrue(payload["oracle_identity_matches"])
        self.assertIn("node-coverage decision", payload["rtdl_role"])
        self.assertIn("not force-vector reduction", payload["boundary"])

    def test_optix_node_coverage_failure_keeps_scalar_identity_boundary(self) -> None:
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", return_value=_PartialPreparedNodeCoverage()):
            payload = app.run_app(
                "optix",
                optix_summary_mode="node_coverage_prepared",
                node_radius=app.NODE_DISCOVERY_RADIUS,
                require_rt_core=True,
            )

        self.assertFalse(payload["node_coverage"]["all_bodies_have_node_candidate"])
        self.assertIsNone(payload["node_coverage"]["uncovered_body_ids"])
        self.assertFalse(payload["node_coverage"]["identity_parity_available"])
        self.assertFalse(payload["matches_oracle"])
        self.assertFalse(payload["oracle_decision_matches"])
        self.assertIsNone(payload["oracle_identity_matches"])

    def test_require_rt_core_rejects_default_rows(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "node_coverage_prepared"):
            app.run_app("optix", require_rt_core=True)

    def test_negative_node_radius_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "node_radius must be non-negative"):
            app.run_app("optix", optix_summary_mode="node_coverage_prepared", node_radius=-0.1)

    def test_missing_rows_are_uncovered(self) -> None:
        bodies = app.make_bodies()
        rows = (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
        )

        summary = app._node_coverage_from_count_rows(
            rows,
            bodies=bodies,
            radius=app.NODE_DISCOVERY_RADIUS,
        )

        self.assertFalse(summary["all_bodies_have_node_candidate"])
        self.assertEqual(summary["uncovered_body_ids"], [2, 3, 4, 5, 6])
        self.assertEqual(summary["covered_body_count"], 1)


if __name__ == "__main__":
    unittest.main()
