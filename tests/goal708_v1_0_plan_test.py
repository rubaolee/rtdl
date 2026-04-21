from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal708_v1_0_embree_then_nvidia_rt_core_plan_2026-04-21.md"


class Goal708V10PlanTest(unittest.TestCase):
    def test_plan_records_two_stage_direction(self):
        text = REPORT.read_text()
        self.assertIn("First, make Embree the mature local CPU RT baseline.", text)
        self.assertIn("Then, move selected public apps to genuine NVIDIA RT-core execution", text)
        self.assertIn("`v0.9.8`: development milestone.", text)
        self.assertIn("`v0.9.9`: internal pre-release boosting milestone.", text)
        self.assertIn("`v1.0`: public claim milestone.", text)
        self.assertIn("Do not rent or keep an RTX cloud instance for broad app benchmarking yet.", text)

    def test_plan_requires_rtdl_controlled_embree_parallelism(self):
        text = REPORT.read_text()
        required = [
            "Embree itself does not automatically make every RTDL app multi-threaded.",
            "RTDL-controlled Embree parallel dispatch",
            "RTDL_EMBREE_THREADS=<N|auto|1>",
            "Partition query units into contiguous index ranges",
            "Merge per-thread row vectors deterministically",
            "Treat committed Embree scenes as read-only during dispatch.",
            "Preserve row ordering and exact parity against CPU reference.",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_plan_preserves_nvidia_rt_core_claim_boundary(self):
        text = REPORT.read_text()
        compact_text = " ".join(text.split())
        required = [
            "uses OptiX traversal, such as `optixTrace`, over an OptiX acceleration structure",
            "ran on RTX-class NVIDIA hardware",
            "splits native traversal from Python packing",
            "CUDA-through-OptiX row paths",
            "Host-indexed fallback paths",
        ]
        for phrase in required:
            self.assertIn(phrase, compact_text)

    def test_plan_resolves_first_embree_kernel_family(self):
        text = REPORT.read_text()
        self.assertIn("Fixed-radius/KNN point queries go first for the Embree stage.", text)
        self.assertIn("Ray hit-count / closest-hit / any-hit go second.", text)
        self.assertLess(
            text.index("- fixed-radius and KNN point queries"),
            text.index("- ray hit-count / closest-hit / any-hit"),
        )

    def test_plan_gates_optix_work_and_windows_perf_floors(self):
        text = REPORT.read_text()
        required = [
            "Goal 712 may not begin until Goal 711 passes for at least the robot collision",
            "Goal 714: v0.9.8 Full Development/Test Closure",
            "Goal 715: v0.9.9 Internal Pre-Release Boosting",
            "Fixed-radius and KNN: at least 50,000 query points",
            "Ray kernels: at least 100,000 rays.",
            "Graph BFS: at least 10,000 frontier nodes",
            "DB scan/aggregation: at least 500,000 candidate rows.",
        ]
        for phrase in required:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
