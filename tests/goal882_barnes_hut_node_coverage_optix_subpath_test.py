from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_barnes_hut_force_app as app


class _PreparedNodeCoverage:
    def __call__(
        self,
        *,
        search_points,
        query_points,
        radius: float,
        threshold: int,
        backend: str,
        max_radius: float,
        prepare_scene,
    ):
        self.body_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        self.backend = backend
        self.max_radius = max_radius
        return {
            "primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
            "summary_primitive": "REDUCE_INT(COUNT)",
            "threshold_reached_count": len(query_points),
        }


class _PartialPreparedNodeCoverage(_PreparedNodeCoverage):
    def __call__(self, **kwargs):
        result = super().__call__(**kwargs)
        result["threshold_reached_count"] = max(0, self.body_count - 1)
        return result


class Goal882BarnesHutNodeCoverageOptixSubpathTest(unittest.TestCase):
    def test_optix_node_coverage_mode_uses_prepared_traversal(self) -> None:
        prepared = _PreparedNodeCoverage()
        with mock.patch.object(
            app.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=prepared,
        ) as mocked:
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
        self.assertEqual(prepared.backend, "optix")
        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["node_coverage"]["all_bodies_have_node_candidate"])
        self.assertEqual(payload["node_coverage"]["summary_mode"], "scalar_threshold_count")
        self.assertEqual(payload["node_coverage"]["generic_primitive"], "FIXED_RADIUS_COUNT_THRESHOLD_2D")
        self.assertEqual(payload["node_coverage"]["summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertIsNone(payload["node_coverage"]["row_count"])
        self.assertTrue(payload["node_coverage"]["identity_parity_available"])
        self.assertTrue(payload["matches_oracle"])
        self.assertTrue(payload["oracle_decision_matches"])
        self.assertTrue(payload["oracle_identity_matches"])
        self.assertIn("node-coverage decision", payload["rtdl_role"])
        self.assertIn("not force-vector reduction", payload["boundary"])

    def test_optix_node_coverage_failure_keeps_scalar_identity_boundary(self) -> None:
        with mock.patch.object(
            app.rt,
            "run_generic_prepared_fixed_radius_threshold_reached_count_2d",
            side_effect=_PartialPreparedNodeCoverage(),
        ):
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
