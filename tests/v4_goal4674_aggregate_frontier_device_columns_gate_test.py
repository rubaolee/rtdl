from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "future" / "v4" / "evidence" / (
    "v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.json"
)
REPORT = ROOT / "future" / "v4" / (
    "v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.md"
)
CALL_FOR_REVIEW = ROOT / "future" / "v4" / "reviews" / (
    "call_for_review_v4_goal4674_aggregate_frontier_device_columns_static_protocol_gate_2026-06-25.md"
)
REVIEW_DEBT = ROOT / "future" / "v4" / "reviews" / "v4_goal4674_review_debt_2026-06-25.md"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"

sys.path.insert(0, str(ROOT / "src"))


class V4Goal4674AggregateFrontierDeviceColumnsGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_gate_passes_only_for_local_goal4675_not_pod(self) -> None:
        self.assertEqual(
            "aggregate_frontier_device_columns_static_protocol_gate_pass__goal4675_local_runner_authorized__pod_not_authorized",
            self.payload["decision_label"],
        )
        auth = self.payload["goal4675_authorization"]
        self.assertTrue(auth["local_runner_productization_authorized"])
        self.assertFalse(auth["pod_run_authorized"])
        self.assertFalse(auth["public_claim_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["pod_run_authorized_by_goal4674"])
        self.assertFalse(self.payload["claim_boundary"]["whole_app_high_performance_wording_authorized"])

    def test_contract_is_app_generic_and_forbids_host_frontier_handoff(self) -> None:
        import rtdsl as rt

        contract = rt.validate_aggregate_frontier_device_columns_native_abi_contract()
        self.assertEqual("AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D", contract["primitive"])
        self.assertTrue(contract["app_generic"])
        self.assertTrue(contract["handoff_contract"]["device_resident_payload_required"])
        self.assertTrue(contract["handoff_contract"]["host_row_materialization_before_partner_forbidden"])
        self.assertIn("frontier_i64_rows_host_tuple", contract["hot_path_forbidden_outputs"])
        self.assertFalse(contract["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(contract["claim_boundary"]["rt_core_speedup_claim_authorized"])

    def test_native_device_column_body_does_not_wrap_old_host_row_collector(self) -> None:
        api = API.read_text(encoding="utf-8")
        start = api.index("extern \"C\" int rtdl_optix_prepare_aggregate_frontier_device_columns_2d")
        end = api.index("extern \"C\" int rtdl_optix_prepare_aggregate_tree_fused_weighted_vector_sum_2d")
        body = api[start:end]
        for forbidden in (
            "rtdl_optix_collect_aggregate_frontier_2d(",
            "frontier_rows_out",
            "std::vector<int64_t> frontier_rows",
        ):
            self.assertNotIn(forbidden, body)
        for required in (
            "g_aggregate_frontier_device_columns_2d.count_fn",
            "g_aggregate_frontier_device_columns_2d.prefix_fn",
            "g_aggregate_frontier_device_columns_2d.write_fn",
            "cuLaunchKernel",
            "row_offsets",
            "source_ids_device_ptr",
        ):
            self.assertIn(required, body)

    def test_native_symbols_are_declared_and_runtime_metadata_blocks_host_materialization(self) -> None:
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_prepare_aggregate_frontier_device_columns_2d",
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            "rtdl_optix_destroy_aggregate_frontier_device_columns_2d",
        ):
            self.assertIn(symbol, api)
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, runtime)
        self.assertIn('"frontier_columns_materialized_on_host": False', runtime)
        self.assertIn('"row_offsets_materialized_on_host": False', runtime)

    def test_denominators_distinguish_v2_14_absence_from_v3_0_2_presence(self) -> None:
        denominators = self.payload["version_denominators"]
        self.assertEqual(
            "logical_family_present_device_column_primitive_absent",
            denominators["v2_14"]["classification"],
        )
        self.assertIn(
            "rtdl_optix_collect_aggregate_frontier_2d",
            denominators["v2_14"]["symbols_confirmed_present"],
        )
        self.assertIn(
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            denominators["v2_14"]["symbols_confirmed_absent"],
        )
        self.assertEqual("device_column_primitive_present", denominators["v3_0_2"]["classification"])
        self.assertIn(
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            denominators["v3_0_2"]["symbols_confirmed_present"],
        )

    def test_correctness_contract_and_bars_are_frozen(self) -> None:
        correctness = self.payload["frozen_correctness_contract"]
        self.assertTrue(correctness["aggregate_frontier_row_parity_required"])
        self.assertTrue(correctness["row_offsets_parity_required"])
        self.assertTrue(correctness["downstream_summary_parity_required"])
        self.assertIn("frontier_rows_host_dicts", correctness["forbidden_hot_path_outputs_before_partner"])
        bars = self.payload["frozen_later_pod_bars_if_goal4676_is_authorized"]
        self.assertEqual(1.2, bars["aggregate_frontier_hot_v4_over_v2_14_min"])
        self.assertEqual(1.1, bars["aggregate_frontier_wall_v4_over_v2_14_min"])
        self.assertFalse(bars["host_frontier_materialization_in_hot_path_allowed"])
        self.assertFalse(bars["partner_migration_counts_as_speed"])

    def test_report_and_review_debt_preserve_non_authorization(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        call = CALL_FOR_REVIEW.read_text(encoding="utf-8")
        debt = REVIEW_DEBT.read_text(encoding="utf-8")
        self.assertIn("Goal4674 passes the local static/protocol gate", report)
        self.assertIn("This authorizes only Goal4675 local runner productization", report)
        self.assertIn("does not authorize POD benchmarking", report)
        self.assertIn("Non-Authorization", report)
        self.assertIn("Expected Non-Authorization", call)
        self.assertIn("review_debt_recorded_no_release_authorization", debt)


if __name__ == "__main__":
    unittest.main()
