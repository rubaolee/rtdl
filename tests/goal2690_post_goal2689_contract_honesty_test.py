from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]
RAYDB_APP = ROOT / "examples/v2_0/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py"


class Goal2690PostGoal2689ContractHonestyTest(unittest.TestCase):
    def test_raydb_v25_paths_do_not_use_ready_or_promoted_wording(self) -> None:
        source = RAYDB_APP.read_text(encoding="utf-8")

        self.assertNotIn('"native_rt_core_lowering_ready": True', source)
        self.assertNotIn("promoted_performance_path=True", source)
        self.assertIn('"native_rt_core_lowering_path_present": True', source)
        self.assertIn('"native_rt_core_lowering_ready": False', source)

    def test_raydb_hit_stream_result_uses_tolerance_policy_and_safe_readiness(self) -> None:
        fixture = raydb.make_fixture(copies=1)
        plan = raydb.make_plan("sum")
        payload = raydb._run_paper_rt_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode="sum",
            copies=1,
            backend="cpu",
            backend_label="paper_rt_cpu_hit_stream_reference",
            allow_reference_fallback=True,
        )
        metadata = payload["metadata"]

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(
            metadata["cpu_reference_match_policy"]["numeric_policy"],
            "exact_for_integral_values_otherwise_isclose",
        )
        self.assertTrue(metadata["native_rt_core_lowering_path_present"])
        self.assertFalse(metadata["native_rt_core_lowering_ready"])
        self.assertFalse(metadata["v2_4_phase_timing"]["promoted_performance_path"])

    def test_raydb_device_handoff_result_uses_tolerance_policy_and_safe_readiness(self) -> None:
        fixture = raydb.make_fixture(copies=1)
        plan = raydb.make_plan("sum")
        payload = raydb._run_paper_rt_device_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode="sum",
            copies=1,
            backend="cpu",
            backend_label="paper_rt_cpu_device_hit_stream_reference",
            allow_reference_fallback=True,
        )
        metadata = payload["metadata"]

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertIn("cpu_reference_match_policy", metadata)
        self.assertTrue(metadata["native_rt_core_lowering_path_present"])
        self.assertFalse(metadata["native_rt_core_lowering_ready"])
        self.assertFalse(metadata["hit_stream_handoff"]["removes_host_materialization_bottleneck"])


if __name__ == "__main__":
    unittest.main()
