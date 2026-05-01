from __future__ import annotations

import unittest


class Goal977OptixOnlyArtifactIntakeTest(unittest.TestCase):
    def test_targets_exact_remaining_optix_only_baselines(self) -> None:
        module = __import__("scripts.goal977_optix_only_artifact_intake", fromlist=["GRAPH_BASELINES", "_artifact_path"])
        self.assertEqual(
            set(module.GRAPH_BASELINES),
            {
                "optix_visibility_anyhit",
                "optix_native_graph_ray_bfs",
                "optix_native_graph_ray_triangle_count",
            },
        )
        targets = (
            (
                "graph_analytics",
                "graph_visibility_edges_gate",
                "optix_visibility_anyhit",
            ),
            (
                "graph_analytics",
                "graph_visibility_edges_gate",
                "optix_native_graph_ray_bfs",
            ),
            (
                "graph_analytics",
                "graph_visibility_edges_gate",
                "optix_native_graph_ray_triangle_count",
            ),
            (
                "segment_polygon_anyhit_rows",
                "segment_polygon_anyhit_rows_prepared_bounded_gate",
                "optix_prepared_bounded_pair_rows",
            ),
        )
        for app, path_name, baseline in targets:
            with self.subTest(app=app, path_name=path_name, baseline=baseline):
                row = module.load_goal835_row(app=app, path_name=path_name, baseline_name=baseline)
                path = module._artifact_path(app, path_name, baseline)
                self.assertIn(baseline, row["required_baselines"])
                self.assertEqual(path.name, f"goal835_baseline_{app}_{path_name}_{baseline}_2026-04-23.json")

    def test_source_artifacts_are_strict_pass_before_intake(self) -> None:
        module = __import__("scripts.goal977_optix_only_artifact_intake", fromlist=["DEFAULT_CLOUD_DIR", "_load_json"])
        graph = module._load_json(module.DEFAULT_CLOUD_DIR / "goal889_graph_visibility_optix_gate_rtx.json")
        segment = module._load_json(module.DEFAULT_CLOUD_DIR / "goal934_segment_polygon_anyhit_rows_prepared_bounded_rtx.json")
        self.assertIs(graph["strict_pass"], True)
        self.assertEqual(graph["strict_failures"], [])
        self.assertIs(segment["strict_pass"], True)
        self.assertEqual(segment["strict_failures"], [])
        self.assertIs(segment["result"]["matches_oracle"], True)
        self.assertIs(segment["result"]["overflowed"], False)


if __name__ == "__main__":
    unittest.main()
