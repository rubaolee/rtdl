import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal5211GlobalBoundEarlyBreakContractTest(unittest.TestCase):
    def test_native_v5_declares_generic_global_bound_early_break(self) -> None:
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5", api)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5", prelude)
        self.assertIn("global_bound_early_break", workloads)
        self.assertIn("global_bound_distance_bits", workloads)
        self.assertIn("global_bound_early_break_count", workloads)
        self.assertIn("atomicMax(params.global_bound_distance_bits", workloads)
        self.assertIn("optixSetPayload_6(1u)", workloads)
        self.assertIn("optixSetPayload_6(2u)", workloads)
        self.assertIn("if (kind == 2)", workloads)
        self.assertIn("optixTerminateRay()", workloads)
        self.assertIn('nullptr, 7).release();', workloads)

        kernel_start = workloads.index("static const char* kCellMbrFrontier3DKernelSrc")
        kernel_end = workloads.index("static void ensure_cell_mbr_frontier_3d_pipeline")
        kernel = workloads[kernel_start:kernel_end].lower()
        for forbidden in ("xhd", "x-hd", "paper", "author"):
            self.assertNotIn(forbidden, kernel)

    def test_python_runtime_requires_v5_and_labels_approximate_witness_contract(self) -> None:
        runtime = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        fn_start = runtime.index("def collect_cell_mbr_nearest_frontier_3d_optix")
        fn_end = runtime.index("@dataclass(frozen=True)", fn_start)
        window = runtime[fn_start:fn_end]

        self.assertIn("global_bound_early_break: bool = False", window)
        self.assertIn("global_bound_early_break requires inline_nearest=True", window)
        self.assertIn("rtdl_optix_collect_cell_mbr_nearest_frontier_3d_v5", window)
        self.assertIn("generic_max_nearest_global_bound_early_break", window)
        self.assertIn("per_source_witness_exact", window)
        self.assertIn(
            "native_inline_cell_point_nearest_with_global_bound_early_break_for_max_nearest_reductions",
            window,
        )

    def test_column_frontdoor_and_xhd_gate_expose_explicit_flag(self) -> None:
        partner = (ROOT / "src/rtdsl/partner_continuations.py").read_text(encoding="utf-8")
        frontdoor_start = partner.index("def cell_mbr_nearest_frontier_native_3d_optix_columns")
        frontdoor_end = partner.index("def nearest_witness_from_cell_mbr_frontier_numpy_columns", frontdoor_start)
        frontdoor = partner[frontdoor_start:frontdoor_end]
        self.assertIn("global_bound_early_break: bool = False", frontdoor)
        self.assertIn("global_bound_early_break=bool(global_bound_early_break)", frontdoor)
        self.assertIn('"global_bound_contract": native.get("global_bound_contract")', frontdoor)
        self.assertIn('"per_source_witness_exact": native.get("per_source_witness_exact")', frontdoor)

        gate = (
            ROOT / "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_cell_mbr_frontier_route_gate.py"
        ).read_text(encoding="utf-8")
        self.assertIn("--global-bound-early-break", gate)
        self.assertIn("global_bound_early_break=bool(global_bound_early_break)", gate)
        self.assertIn('"global_bound_early_break_count"', gate)
        self.assertIn('"per_source_witness_exact"', gate)

        subset_gate = (
            ROOT / "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_full_public_subset_scaling_gate.py"
        ).read_text(encoding="utf-8")
        self.assertIn("--global-bound-early-break", subset_gate)
        self.assertIn("global_bound_early_break=bool(getattr(args, \"global_bound_early_break\", False))", subset_gate)


if __name__ == "__main__":
    unittest.main()
