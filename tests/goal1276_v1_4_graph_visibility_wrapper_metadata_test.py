from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_graph_analytics_app as graph_app
import rtdsl as rt


class _FakePreparedScene:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def count(self, prepared_rays):
        return 3


class _FakePreparedRays:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class Goal1276V14GraphVisibilityWrapperMetadataTest(unittest.TestCase):
    def test_prepared_anyhit_count_wrapper_delegates_to_supplied_backend_factories(self) -> None:
        result = rt.run_prepared_visibility_anyhit_count(
            blockers=("blockers",),
            rays=("rays",),
            prepare_scene=lambda blockers: _FakePreparedScene(),
            prepare_rays=lambda rays: _FakePreparedRays(),
            visibility_query_repeats=2,
        )

        self.assertEqual(result["blocked_count"], 3)
        self.assertIn("scene_prepare_sec", result["run_phases"])
        self.assertIn("ray_prepare_sec", result["run_phases"])
        self.assertIn("query_anyhit_count_sec", result["run_phases"])
        self.assertGreaterEqual(result["run_phases"]["query_anyhit_count_sec"], 0.0)

    def test_contract_helper_defines_v1_4_graph_visibility_scope(self) -> None:
        contract = rt.visibility_edges_primitive_contract(
            backend="optix",
            output_mode="summary",
            prepared_summary=True,
        )

        self.assertEqual(contract["app_row"], "graph_analytics.visibility_edges")
        self.assertEqual(contract["primitive"], "ANY_HIT")
        self.assertEqual(contract["summary_primitive"], "COUNT_HITS")
        self.assertEqual(contract["alternate_summary_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(contract["backend_scope"], ("embree", "optix"))
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertEqual(contract["backend_contract_role"], "nvidia_rt_target")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertEqual(contract["mode"], "prepared")
        self.assertEqual(contract["prepared_state"], "build_geometry_and_probe_rays_reusable")
        self.assertIn("BFS", contract["claim_boundary"])
        self.assertEqual(contract["migration_status"], "compatibility_wrapper_metadata_only")

    def test_cpu_visibility_summary_attaches_one_shot_contract_without_changing_counts(self) -> None:
        payload = graph_app.run_app(
            "cpu_python_reference",
            scenario="visibility_edges",
            copies=1,
            output_mode="summary",
        )
        section = payload["sections"]["visibility_edges"]
        contract = section["primitive_contract"]

        self.assertEqual(section["summary"], {"visible_edge_count": 1, "blocked_edge_count": 3})
        self.assertEqual(contract["backend"], "cpu_python_reference")
        self.assertFalse(contract["active_v1_4_backend"])
        self.assertEqual(contract["backend_contract_role"], "compatibility_or_inactive")
        self.assertFalse(contract["same_contract_baseline_required"])
        self.assertEqual(contract["mode"], "one_shot")
        self.assertEqual(contract["summary_primitive"], "COUNT_HITS")
        self.assertIn("query_visibility_pair_rows_sec", section["run_phases"])

    def test_mocked_optix_summary_attaches_prepared_contract_and_preserves_fast_path(self) -> None:
        with (
            mock.patch.object(graph_app.rt, "prepare_optix_ray_triangle_any_hit_2d", return_value=_FakePreparedScene()),
            mock.patch.object(graph_app.rt, "prepare_optix_rays_2d", return_value=_FakePreparedRays()),
            mock.patch.object(graph_app.rt, "visibility_pair_rows") as visibility_pair_rows,
        ):
            payload = graph_app.run_app(
                "optix",
                scenario="visibility_edges",
                copies=1,
                output_mode="summary",
            )

        section = payload["sections"]["visibility_edges"]
        contract = section["primitive_contract"]
        visibility_pair_rows.assert_not_called()
        self.assertEqual(section["native_continuation_backend"], "optix_prepared_visibility_anyhit_count")
        self.assertEqual(contract["backend"], "optix")
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertEqual(contract["backend_contract_role"], "nvidia_rt_target")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertEqual(contract["mode"], "prepared")
        self.assertEqual(contract["prepared_state"], "build_geometry_and_probe_rays_reusable")
        self.assertIn("query_anyhit_count_sec", contract["phase_counters"])

    def test_mocked_embree_summary_attaches_cpu_rt_baseline_contract(self) -> None:
        rows = (
            {"observer_id": 1, "target_id": 10, "visible": 0},
            {"observer_id": 1, "target_id": 11, "visible": 0},
            {"observer_id": 2, "target_id": 10, "visible": 0},
            {"observer_id": 2, "target_id": 11, "visible": 1},
        )
        with mock.patch.object(graph_app.rt, "visibility_pair_rows", return_value=rows) as visibility_pair_rows:
            payload = graph_app.run_app(
                "embree",
                scenario="visibility_edges",
                copies=1,
                output_mode="summary",
            )

        section = payload["sections"]["visibility_edges"]
        contract = section["primitive_contract"]
        visibility_pair_rows.assert_called_once()
        self.assertEqual(section["summary"], {"visible_edge_count": 1, "blocked_edge_count": 3})
        self.assertEqual(section["native_continuation_backend"], "none")
        self.assertEqual(contract["backend"], "embree")
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertEqual(contract["backend_contract_role"], "cpu_rt_baseline_and_fallback")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertEqual(contract["mode"], "one_shot")
        self.assertEqual(contract["prepared_state"], "none_required_for_row_materialization")


if __name__ == "__main__":
    unittest.main()
