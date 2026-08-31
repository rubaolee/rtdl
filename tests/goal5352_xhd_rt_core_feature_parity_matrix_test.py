import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5352_rt_core_feature_parity_matrix.json"
SCRIPT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "build_xhd_goal5352_rt_core_parity_matrix.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("goal5352_builder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5352XhdRtCoreFeatureParityMatrixTest(unittest.TestCase):
    def load_artifact(self):
        with ARTIFACT.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_artifact_keeps_rt_core_parity_not_closed(self):
        payload = self.load_artifact()
        self.assertEqual(
            payload["status"],
            "rt_core_feature_parity_matrix_ready__author_rt_algorithm_parity_not_closed",
        )
        rollup = payload["same_functionality_rollup"]
        self.assertFalse(rollup["author_rt_core_algorithm_parity_ready"])
        self.assertFalse(rollup["full_xhd_paper_reproduction_ready"])
        self.assertEqual([], rollup["closed_features"])
        self.assertIn("radius_growth_and_tune_radius", rollup["not_closed_features"])
        self.assertIn("load_balance_and_heavy_cell_offload", rollup["not_closed_features"])

    def test_wrapper_surface_does_not_silently_claim_author_rt_options(self):
        payload = self.load_artifact()
        surface = payload["current_wrapper_surface"]
        self.assertFalse(surface["all_author_rt_options_observed"])
        self.assertNotIn("radius", surface["author_rt_option_surface_observed"])
        for flag in [
            "fast_build_bvh",
            "rebuild_bvh",
            "eb",
            "prune",
            "lb",
            "n_points_cell",
            "tune_grid",
            "tune_radius",
        ]:
            self.assertIn(flag, surface["author_rt_option_surface_observed"])
            self.assertFalse(surface["author_rt_option_surface_observed"][flag])
        self.assertIn("cell-mbr-exact-witness", surface["rtdl_route_labels"])
        self.assertIn("cell-mbr-fast-scalar", surface["rtdl_route_labels"])

    def test_feature_matrix_has_expected_blocking_author_rt_features(self):
        payload = self.load_artifact()
        by_key = {row["key"]: row for row in payload["feature_matrix"]}
        expected = {
            "rt_variant_value_surface",
            "author_rt_option_surface",
            "uniform_grid_and_cell_mbr_target_structure",
            "radius_growth_and_tune_radius",
            "early_break_prune_scalar_contract",
            "load_balance_and_heavy_cell_offload",
            "figure11_memory_fields",
            "figure5_author_variant_performance_matrix",
            "exact_paper_input_identity",
        }
        self.assertTrue(expected.issubset(by_key))
        for key in expected:
            self.assertTrue(by_key[key]["blocking_for_full_functionality"], key)
            self.assertNotIn(by_key[key]["same_functionality_status"], {"closed", "implemented_and_reviewed"})

    def test_claim_boundaries_all_false(self):
        payload = self.load_artifact()
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)

    def test_recommended_targets_prioritize_rt_algorithm_not_variant_plumbing(self):
        payload = self.load_artifact()
        targets = payload["recommended_next_targets"]
        self.assertEqual("author_rt_option_surface_gate", targets[0]["target"])
        self.assertEqual("radius_growth_and_tune_radius_semantics", targets[1]["target"])
        self.assertEqual("load_balance_heavy_offload_denominator_gate", targets[2]["target"])
        self.assertNotIn("accept_variant_names", json.dumps(targets))

    def test_builder_recreates_schema_and_exit_label(self):
        builder = _load_builder()
        rebuilt = builder.build_matrix()
        self.assertEqual(
            rebuilt["schema"],
            "rtdl.paper_reproduction.xhd.goal5352.rt_core_feature_parity_matrix.v1",
        )
        self.assertEqual(
            rebuilt["exit_label"],
            "rt_core_feature_parity_matrix_ready__next_target_author_rt_option_surface",
        )


if __name__ == "__main__":
    unittest.main()
