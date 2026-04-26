from __future__ import annotations

import unittest


class Goal975LinuxPostgisRemainingBaselinesTest(unittest.TestCase):
    def test_collector_targets_exact_remaining_postgis_baselines(self) -> None:
        module = __import__(
            "scripts.goal975_linux_postgis_remaining_baselines",
            fromlist=["_artifact_path"],
        )
        expected = {
            (
                "road_hazard_screening",
                "road_hazard_native_summary_gate",
                "postgis_when_available",
            ),
            (
                "segment_polygon_hitcount",
                "segment_polygon_hitcount_native_experimental",
                "postgis_when_available",
            ),
            (
                "segment_polygon_anyhit_rows",
                "segment_polygon_anyhit_rows_prepared_bounded_gate",
                "postgis_when_available_for_same_pair_semantics",
            ),
            (
                "polygon_pair_overlap_area_rows",
                "polygon_pair_overlap_optix_native_assisted_phase_gate",
                "postgis_when_available_for_same_unit_cell_contract",
            ),
            (
                "polygon_set_jaccard",
                "polygon_set_jaccard_optix_native_assisted_phase_gate",
                "postgis_when_available_for_same_unit_cell_contract",
            ),
        }
        for app, path_name, baseline in expected:
            with self.subTest(app=app, path_name=path_name, baseline=baseline):
                row = module.load_goal835_row(app=app, path_name=path_name, baseline_name=baseline)
                artifact_path = module._artifact_path(app, path_name, baseline)
                self.assertIn(baseline, row["required_baselines"])
                self.assertEqual(artifact_path.name, f"goal835_baseline_{app}_{path_name}_{baseline}_2026-04-23.json")

    def test_phase_helpers_cover_required_gate_fields(self) -> None:
        module = __import__(
            "scripts.goal975_linux_postgis_remaining_baselines",
            fromlist=["_anyhit_phase", "_polygon_phase", "_segpoly_phase"],
        )
        self.assertEqual(
            set(module._segpoly_phase(1.0, [2.0], 0.25)),
            {
                "input_build_sec",
                "optix_prepare_sec",
                "optix_query_sec",
                "python_postprocess_sec",
                "validation_sec",
                "optix_close_sec",
            },
        )
        self.assertEqual(
            set(module._anyhit_phase(1.0, [2.0], 3, parity=True)),
            {
                "input_build_sec",
                "cpu_reference_total_sec",
                "optix_prepare_sec",
                "optix_query_sec",
                "python_postprocess_sec",
                "validation_sec",
                "optix_close_sec",
                "emitted_count",
                "copied_count",
                "overflowed",
                "strict_pass",
                "strict_failures",
                "status",
            },
        )
        self.assertEqual(
            set(module._polygon_phase(1.0, [2.0], parity=True)),
            {
                "input_build_sec",
                "cpu_reference_sec",
                "optix_candidate_discovery_sec",
                "cpu_exact_refinement_sec",
                "native_exact_continuation_sec",
                "parity_vs_cpu",
                "rt_core_candidate_discovery_active",
            },
        )


if __name__ == "__main__":
    unittest.main()
