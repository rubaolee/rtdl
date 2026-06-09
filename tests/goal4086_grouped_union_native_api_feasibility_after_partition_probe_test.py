from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4086_grouped_union_native_api_feasibility_after_partition_probe_2026-06-09.md"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal4086GroupedUnionNativeApiFeasibilityTest(unittest.TestCase):
    def test_report_records_goal4085_blocking_build_cost(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "0.219861s clustered",
            "0.201510s road",
            "0.367637s ngsim",
            "cannot become a fast partition-aware route through a thin wrapper",
            "Contiguous query-range blocking is not enough",
            "prepared_fixed_radius_partition_convergence_grouped_union_3d",
        ]:
            self.assertIn(fragment, report)

    def test_current_abi_has_query_ranges_but_no_partition_pair_stream(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        combined = api + "\n" + prelude

        self.assertIn("rtdl_optix_apply_prepared_fixed_radius_grouped_union_3d_self_range_device_outputs", combined)
        self.assertIn("size_t query_start", combined)
        self.assertIn("size_t query_count", combined)
        self.assertIn("size_t query_index_offset", combined)

        native_exports = re.findall(
            r"rtdl_optix_[a-z0-9_]*fixed_radius_grouped_union_3d[a-z0-9_]*",
            combined,
        )
        self.assertTrue(native_exports)
        self.assertFalse(any("partition" in symbol for symbol in native_exports))
        self.assertNotIn("partition_pair", combined)
        self.assertNotIn("safe_full_partition", combined)
        self.assertNotIn("ambiguous_partition", combined)

    def test_kernel_param_block_lacks_partition_work_stream_fields(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        start = core.index("struct FixedRadiusGroupedUnion3DRtParams")
        end = core.index("};", start)
        params = core[start:end]

        for fragment in [
            "query_points",
            "search_points",
            "query_count",
            "query_index_offset",
            "item_count",
            "same_root_culling",
            "direct_side_effect",
        ]:
            self.assertIn(fragment, params)

        for fragment in [
            "partition",
            "safe_full",
            "ambiguous",
            "pair_offsets",
            "work_stream",
        ]:
            self.assertNotIn(fragment, params)

    def test_report_keeps_app_agnostic_and_claim_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for forbidden in [
            "does not add a native ABI",
            "promote a candidate",
            "public speedup wording",
            "automatic partner selection",
            "app-specific native-engine logic",
        ]:
            self.assertIn(forbidden, report)
        self.assertIn("Forbidden native/runtime vocabulary", report)
        self.assertIn("DBSCAN", report)


if __name__ == "__main__":
    unittest.main()
