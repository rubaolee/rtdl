import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
SCRIPT = ROOT / "scripts" / "goal1657_v1_6_x_optix_collect_k_four_way_merge_probe.py"


class Goal1657OptixCollectKFourWayMergeProbeIntakeTest(unittest.TestCase):
    def test_native_probe_is_diagnostic_only(self) -> None:
        api = API.read_text(encoding="utf-8")
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_four_way_merge_probe", api)
        self.assertIn("collect_k_bounded_i64_row_width2_four_way_materialize_mark_counts_derived", core)
        self.assertIn("g_collect_k_i64_row_width2_four_way_materialize_mark_counts_derived", core)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_FOUR_WAY_MERGE", api)
        self.assertNotIn("collect_k_use_four_way_merge", api)

    def test_probe_script_declares_native_abi_and_claim_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_four_way_merge_probe", text)
        self.assertIn("Diagnostic four-way collect-k merge probe only", text)
        self.assertIn("not a production", text)
        self.assertIn("not a public speedup claim", text)

    def test_kernel_uses_stable_segment_order_for_duplicate_rows(self) -> None:
        core = CORE.read_text(encoding="utf-8")

        self.assertIn("peer_slot < segment_slot ? upper : lower", core)
        self.assertIn("has_prior_duplicate", core)
        self.assertIn("atomicAdd(&block_counts", core)


if __name__ == "__main__":
    unittest.main()
