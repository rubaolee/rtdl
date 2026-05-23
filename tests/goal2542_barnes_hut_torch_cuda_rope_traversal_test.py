from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2542_barnes_hut_torch_cuda_rope_traversal_2026-05-23.md"
)
README = REPO_ROOT / "examples" / "v2_0" / "research_benchmarks" / "barnes_hut" / "README.md"
SCRIPT = REPO_ROOT / "scripts" / "goal2542_barnes_hut_torch_cuda_rope_vector_sum.py"
STACK_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_8192_2026-05-23.json"
)
STACK_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2541_barnes_hut_torch_cuda_fused_vector_sum_pod_32768_2026-05-23.json"
)
ROPE_8192 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_8192_2026-05-23.json"
)
ROPE_32768 = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2542_barnes_hut_torch_cuda_rope_vector_sum_pod_32768_2026-05-23.json"
)


class Goal2542BarnesHutTorchCudaRopeTraversalTest(unittest.TestCase):
    def test_script_uses_resume_index_and_no_static_stack(self) -> None:
        text = SCRIPT.read_text()
        self.assertIn("node_resume_index", text)
        self.assertIn("dfs_resume_index_rope", text)
        self.assertIn("fused_frontier_vector_sum_rope_cuda", text)
        self.assertNotIn("kStaticMaxStack", text)

    def test_rope_artifacts_are_correct_against_reference(self) -> None:
        for path in (ROPE_8192, ROPE_32768):
            payload = json.loads(path.read_text())
            with self.subTest(path=path.name):
                self.assertEqual(payload["backend"], "torch_cuda_extension_rope")
                self.assertEqual(payload["traversal"], "dfs_resume_index_rope")
                self.assertFalse(payload["metadata"]["native_engine_app_specific"])
                self.assertFalse(payload["metadata"]["public_speedup_claim_authorized"])
                self.assertEqual(payload["deltas"]["visited_node_total"], 0)
                self.assertEqual(payload["deltas"]["contribution_row_count"], 0)
                self.assertLess(payload["deltas"]["checksum_force_x_abs"], 1.0e-7)
                self.assertLess(payload["deltas"]["checksum_force_y_abs"], 1.0e-7)

    def test_rope_is_not_slower_than_stack_on_recorded_points(self) -> None:
        stack_8192 = json.loads(STACK_8192.read_text())["timing_ms"]["resident_kernel_min"]
        rope_8192 = json.loads(ROPE_8192.read_text())["timing_ms"]["resident_kernel_min"]
        stack_32768 = json.loads(STACK_32768.read_text())["timing_ms"]["resident_kernel_min"]
        rope_32768 = json.loads(ROPE_32768.read_text())["timing_ms"]["resident_kernel_min"]
        self.assertLessEqual(rope_8192, stack_8192)
        self.assertLessEqual(rope_32768, stack_32768)

    def test_report_and_readme_capture_next_bottleneck(self) -> None:
        report_text = REPORT.read_text()
        readme_text = README.read_text()
        for phrase in [
            "resume_index",
            "not public speedup",
            "slightly faster",
            "contains_source",
            "one-thread-per-source",
            "not OptiX",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("goal2542_barnes_hut_torch_cuda_rope_vector_sum.py", readme_text)


if __name__ == "__main__":
    unittest.main()
