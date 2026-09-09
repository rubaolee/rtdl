from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
DIRECT = ROOT / "src/rtdsl/direct_optix_physical.py"
LOWERING = ROOT / "src/rtdsl/action_optix_lowering.py"


class ActionBoundedSelectionFloat32PolicyTest(unittest.TestCase):
    def test_action_pipeline_is_independent_and_stepwise_float32(self) -> None:
        source = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "static RayAnyHitPipeline g_action_bounded_selection_3d_rt;",
            source,
        )
        self.assertIn("action_bounded_selection_3d_stepwise_f32_kernel_source", source)
        self.assertIn("replacement_count != 2", source)
        self.assertIn("const float dx = __fsub_rn(q.x, t.x);", source)
        self.assertIn("const float dx2 = __fmul_rn(dx, dx);", source)
        self.assertIn(
            "const float distance = __fsqrt_rn(__fadd_rn(__fadd_rn(dx2, dy2), dz2));",
            source,
        )
        action_body = source.split(
            "static void ensure_action_bounded_selection_3d_rt_pipeline()", 1
        )[1].split(
            "static void run_prepared_action_bounded_selection_3d_optix", 1
        )[0]
        self.assertIn("g_action_bounded_selection_3d_rt", action_body)
        self.assertNotIn("g_frn3d_rt", action_body)

    def test_numeric_contract_is_public_and_app_agnostic(self) -> None:
        direct = DIRECT.read_text(encoding="utf-8")
        lowering = LOWERING.read_text(encoding="utf-8")
        contract = "stepwise_f32_sub_mul_add_sqrt_v1"
        self.assertIn(contract, direct)
        self.assertNotIn("then_f32_square", direct)
        self.assertIn('"native_numeric_contract": direct_metadata["numeric_contract"]', lowering)
        native_section = WORKLOADS.read_text(encoding="utf-8").split(
            "static std::string action_bounded_selection_3d_stepwise_f32_kernel_source()",
            1,
        )[1].split("struct PreparedMetricKnn3DOptix", 1)[0].lower()
        for forbidden in ("rtnn", "paper", "application"):
            self.assertNotIn(forbidden, native_section)


if __name__ == "__main__":
    unittest.main()
