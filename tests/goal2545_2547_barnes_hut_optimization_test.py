import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2545_2547_barnes_hut_resident_float32_3d_optimization_2026-05-23.md"
RESIDENT_32768 = REPO_ROOT / "docs" / "reports" / "goal2545_barnes_hut_resident_state_pod_32768_2026-05-23.json"
FLOAT32_32768 = REPO_ROOT / "docs" / "reports" / "goal2546_barnes_hut_float32_subtree_pod_32768_r20_2026-05-23.json"
SCALAR_3D_32768 = REPO_ROOT / "docs" / "reports" / "goal2547_barnes_hut_3d_scalar_subtree_pod_authors_input_32768_2026-05-23.json"
SCRIPT_2545 = REPO_ROOT / "scripts" / "goal2545_barnes_hut_resident_state_benchmark.py"
SCRIPT_2546 = REPO_ROOT / "scripts" / "goal2546_barnes_hut_float32_subtree_kernel.py"
SCRIPT_2547 = REPO_ROOT / "scripts" / "goal2547_barnes_hut_3d_scalar_subtree_kernel.py"


class Goal2545To2547BarnesHutOptimizationTest(unittest.TestCase):
    def test_scripts_keep_app_logic_out_of_native_engine(self) -> None:
        for path in (SCRIPT_2545, SCRIPT_2546, SCRIPT_2547):
            text = path.read_text()
            with self.subTest(path=path.name):
                self.assertIn("native_engine_app_specific", text)
                self.assertIn("public_speedup_claim_authorized", text)

    def test_resident_state_artifact_reuses_prepared_state(self) -> None:
        payload = json.loads(RESIDENT_32768.read_text())
        self.assertTrue(payload["metadata"]["prepared_tree_reused"])
        self.assertTrue(payload["metadata"]["prepared_tensors_reused"])
        self.assertLess(payload["timing_ms"]["resident_event_min"], 4.0)
        self.assertLess(payload["timing_ms"]["resident_wall_per_timestep"], 4.0)

    def test_float32_artifact_records_precision_error_and_speed(self) -> None:
        payload = json.loads(FLOAT32_32768.read_text())
        self.assertEqual(payload["precision"], "float32_accumulation")
        self.assertEqual(payload["deltas"]["visited_node_total"], 0)
        self.assertEqual(payload["deltas"]["contribution_row_count"], 0)
        self.assertLess(payload["timing_ms"]["resident_kernel_min"], 1.0)
        self.assertLess(payload["deltas"]["max_vector_relative_error"], 1.0e-3)
        self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])

    def test_3d_scalar_artifact_is_authors_dimension_but_not_same_tree_claim(self) -> None:
        payload = json.loads(SCALAR_3D_32768.read_text())
        self.assertEqual(payload["contract"], "generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1")
        self.assertTrue(payload["metadata"]["same_dimension_as_authors"])
        self.assertTrue(payload["metadata"]["same_scalar_inverse_square_force_shape_as_authors"])
        self.assertFalse(payload["metadata"]["same_tree_contract_as_authors"])
        self.assertEqual(payload["deltas"]["visited_node_total"], 0)
        self.assertEqual(payload["deltas"]["contribution_row_count"], 0)
        self.assertLess(payload["timing_ms"]["resident_kernel_min"], 1.0)
        self.assertLess(payload["deltas"]["max_scalar_relative_error"], 1.0e-3)

    def test_3d_subtree_range_matches_node_membership(self) -> None:
        from scripts.goal2547_barnes_hut_3d_scalar_subtree_kernel import (
            make_generated_points_3d,
            prepare_arrays_3d,
        )

        points = make_generated_points_3d(256)
        prepared = prepare_arrays_3d(points, bucket_size=16, max_depth=16)
        nodes = tuple(prepared["nodes"])
        source_leaf_node_index = tuple(prepared["source_leaf_node_index"])
        node_subtree_end_index = tuple(prepared["node_subtree_end_index"])
        id_to_index = {point.id: index for index, point in enumerate(points)}
        for node_index, node in enumerate(nodes):
            member_indices = {id_to_index[member_id] for member_id in node.member_ids}
            range_indices = {
                source_index
                for source_index, leaf_index in enumerate(source_leaf_node_index)
                if node_index <= leaf_index < node_subtree_end_index[node_index]
            }
            with self.subTest(node_index=node_index):
                self.assertEqual(range_indices, member_indices)

    def test_report_records_claim_boundary(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "0.473",
            "0.509",
            "6.616",
            "not same tree contract",
            "Not authorized",
            "generic_aggregate_frontier_inverse_square_scalar_sum_3d_v1",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
