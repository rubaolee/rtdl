import unittest
from pathlib import Path
import json


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "goal2544_barnes_hut_torch_cuda_subtree_containment.py"
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2544_barnes_hut_subtree_containment_optimization_2026-05-23.md"
)
BASELINE_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_8192_2026-05-23.json"
)
BASELINE_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_32768_2026-05-23.json"
)
SUBTREE_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2544_barnes_hut_subtree_containment_pod_8192_2026-05-23.json"
)
SUBTREE_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2544_barnes_hut_subtree_containment_pod_32768_2026-05-23.json"
)


class Goal2544BarnesHutSubtreeContainmentTest(unittest.TestCase):
    def test_script_uses_subtree_containment_without_member_scan(self) -> None:
        text = SCRIPT.read_text()
        self.assertIn("source_leaf_dfs_in_node_subtree_range", text)
        self.assertIn("node_subtree_end_index", text)
        self.assertIn("source_leaf_node_index", text)
        self.assertIn("node_index <= source_leaf && source_leaf < subtree_end", text)
        self.assertNotIn("member_indices[offset] == source_index", text)

    def test_subtree_range_matches_node_membership(self) -> None:
        from scripts.goal2544_barnes_hut_torch_cuda_subtree_containment import (
            _prepare_subtree_arrays,
        )

        prepared = _prepare_subtree_arrays(body_count=512, bucket_size=16, max_depth=32)
        nodes = tuple(prepared["tree"]["nodes"])
        source_leaf_node_index = tuple(prepared["source_leaf_node_index"])
        node_subtree_end_index = tuple(prepared["node_subtree_end_index"])
        id_to_index = {body.id: index for index, body in enumerate(prepared["bodies"])}

        for node_index, node in enumerate(nodes):
            member_source_indices = {id_to_index[member_id] for member_id in node.member_ids}
            range_source_indices = {
                source_index
                for source_index, leaf_index in enumerate(source_leaf_node_index)
                if node_index <= leaf_index < node_subtree_end_index[node_index]
            }
            with self.subTest(node_index=node_index):
                self.assertEqual(range_source_indices, member_source_indices)

    def test_pod_artifacts_preserve_reference_contract_and_improve_rope(self) -> None:
        for optimized_path, baseline_path in (
            (SUBTREE_8192, BASELINE_8192),
            (SUBTREE_32768, BASELINE_32768),
        ):
            optimized = json.loads(optimized_path.read_text())
            baseline = json.loads(baseline_path.read_text())
            with self.subTest(path=optimized_path.name):
                self.assertEqual(optimized["backend"], "torch_cuda_extension_subtree_containment")
                self.assertEqual(optimized["containment"], "source_leaf_dfs_in_node_subtree_range")
                self.assertFalse(optimized["metadata"]["native_engine_app_specific"])
                self.assertFalse(optimized["metadata"]["public_speedup_claim_authorized"])
                self.assertEqual(optimized["deltas"]["visited_node_total"], 0)
                self.assertEqual(optimized["deltas"]["contribution_row_count"], 0)
                self.assertLess(optimized["deltas"]["checksum_force_x_abs"], 1.0e-7)
                self.assertLess(optimized["deltas"]["checksum_force_y_abs"], 1.0e-7)
                self.assertLess(
                    optimized["timing_ms"]["resident_kernel_min"],
                    baseline["timing_ms"]["resident_kernel_min"],
                )

    def test_report_records_boundary_and_runtime_lesson(self) -> None:
        text = REPORT.read_text()
        for phrase in [
            "37.036 ms",
            "3.971 ms",
            "not same contract",
            "source_leaf_node_index",
            "node_subtree_end_index",
            "public RTDL-vs-authors speedup claim",
            "not Barnes-Hut app",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
