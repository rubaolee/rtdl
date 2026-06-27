from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_grouped_reduction_m41_local_harness as harness
from rtdsl.numba_partner_continuation import (
    NUMBA_GROUPED_VECTOR_SUM_OFFSETS_STRATEGY_THREAD_PER_GROUP,
)
from rtdsl.numba_partner_continuation import (
    NUMBA_GROUPED_VECTOR_SUM_OFFSETS_STRATEGY_WARP_PER_GROUP_TILED,
)
from rtdsl.numba_partner_continuation import (
    _resolve_numba_grouped_vector_sum_offsets_strategy,
)


class V3PhoenixM41GroupedReductionHarnessTest(unittest.TestCase):
    def test_dry_run_builds_three_variant_harness_without_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = harness.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--dry-run",
                ]
            )
            payload = harness.run_packet(args)

        self.assertEqual(payload["summary"]["status"], harness.STATUS_DRY_RUN_NOT_RELEASE)
        self.assertEqual(set(payload["variants"]), set(harness.ALL_VARIANTS))
        self.assertEqual(payload["comparisons"]["status"], "dry_run_no_performance_interpretation")
        self.assertEqual(payload["summary"]["m41_second_family_selected"], "grouped_vector_sum_2d")
        self.assertFalse(payload["summary"]["release_authorized"])
        self.assertFalse(payload["summary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["summary"]["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["summary"]["all_app_pod_spend_authorized"])
        self.assertFalse(payload["summary"]["focused_pod_spend_authorized_now"])
        self.assertIn("serious-scale free local CUDA", payload["summary"]["focused_pod_spend_conditions"])
        self.assertFalse(payload["summary"]["embedding_work_authorized"])
        self.assertFalse(payload["summary"]["c_abi_work_authorized"])
        self.assertTrue(payload["summary"]["same_rows_per_process"])
        for row in payload["variants"].values():
            self.assertTrue(row["generic_grouped_reduction_contract"])
            self.assertFalse(row["app_specific_route_logic_allowed"])

    def test_serious_scale_and_repeat_gates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            args = harness.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--row-count",
                    "1024",
                    "--dry-run",
                ]
            )
            with self.assertRaises(SystemExit):
                harness.run_packet(args)

            args = harness.parse_args(
                [
                    "--output-dir",
                    tmpdir,
                    "--repeat",
                    "1",
                    "--dry-run",
                ]
            )
            with self.assertRaises(SystemExit):
                harness.run_packet(args)

    def test_source_uses_productized_runner_and_no_app_imports(self) -> None:
        source = Path(harness.__file__).read_text(encoding="utf-8")
        self.assertIn("run_grouped_vector_sum_2d_prepared_session", source)
        self.assertIn("prepare_grouped_vector_sum_2d_partner_columns_session", source)
        self.assertIn("grouped_vector_sum_2d_partner_columns", source)
        self.assertIn("runner_vs_legacy_hot_speedup", source)
        self.assertIn("runner_vs_legacy_wall_speedup", source)
        self.assertIn("all_variant_vector_sum_signatures_allclose", source)
        self.assertIn("adapter_contract_verification", source)
        self.assertIn("_prepared_report_phase_seconds", source)
        self.assertNotIn("research_benchmarks", source)
        self.assertNotIn("raydb", source.lower())

    def test_m43_auto_strategy_targets_original_blocked_shape_not_m42_envelope_shape(self) -> None:
        self.assertEqual(
            _resolve_numba_grouped_vector_sum_offsets_strategy(
                requested="auto",
                row_count=262_144,
                group_count=1_024,
                block_size=256,
            ),
            NUMBA_GROUPED_VECTOR_SUM_OFFSETS_STRATEGY_WARP_PER_GROUP_TILED,
        )
        self.assertEqual(
            _resolve_numba_grouped_vector_sum_offsets_strategy(
                requested="auto",
                row_count=262_144,
                group_count=65_536,
                block_size=256,
            ),
            NUMBA_GROUPED_VECTOR_SUM_OFFSETS_STRATEGY_THREAD_PER_GROUP,
        )

    def test_comparison_payload_exposes_hot_and_wall_without_claim_authorization(self) -> None:
        signature = {
            "group_count": 2,
            "rounded_sha256": "abc",
            "sum_x_values": [1.0, 2.0],
            "sum_y_values": [3.0, 4.0],
        }
        variants = {
            harness.CPU_CONTROL: {
                "status": "ok",
                "generic_grouped_reduction_contract": True,
                "app_specific_route_logic_allowed": False,
                "vector_sum_signature": signature,
                "hot_query_median_sec": 4.0,
                "inclusive_wall_sec": 5.0,
            },
            harness.LEGACY: {
                "status": "ok",
                "generic_grouped_reduction_contract": True,
                "app_specific_route_logic_allowed": False,
                "vector_sum_signature": signature,
                "hot_query_median_sec": 2.0,
                "inclusive_wall_sec": 3.0,
            },
            harness.RUNNER: {
                "status": "ok",
                "generic_grouped_reduction_contract": True,
                "app_specific_route_logic_allowed": False,
                "vector_sum_signature": signature,
                "hot_query_median_sec": 1.0,
                "inclusive_wall_sec": 1.5,
                "runtime_trunk_executes_end_to_end": True,
                "internal_device_residency_between_rtdl_phases": True,
                "hot_path_host_materialization": False,
                "output_counts_match_requested": True,
                "adapter_counts_present": True,
                "output_columns_reused": True,
            },
        }
        comparisons = harness.comparison_payload(variants)

        self.assertTrue(comparisons["all_variant_vector_sum_signatures_match"])
        self.assertTrue(comparisons["all_variant_vector_sum_signatures_allclose"])
        self.assertEqual(comparisons["runner_vs_legacy_hot_speedup"], 2.0)
        self.assertEqual(comparisons["runner_vs_legacy_wall_speedup"], 2.0)
        self.assertEqual(comparisons["runner_vs_cpu_hot_speedup"], 4.0)
        self.assertEqual(comparisons["vector_sum_allclose_tolerance"]["atol"], harness.ALLCLOSE_ATOL)
        self.assertTrue(comparisons["step2_local_runner_contract_candidate"])
        self.assertFalse(comparisons["material_performance_claim_authorized"])

    def test_signature_allclose_accepts_numeric_match_when_hash_differs(self) -> None:
        left = {
            "group_count": 2,
            "rounded_sha256": "left",
            "sum_x_values": [1.0, 2.0],
            "sum_y_values": [3.0, 4.0],
        }
        right = {
            "group_count": 2,
            "rounded_sha256": "right",
            "sum_x_values": [1.0 + 1e-8, 2.0 - 1e-8],
            "sum_y_values": [3.0, 4.0 + 1e-8],
        }

        self.assertTrue(harness._signatures_allclose(left, right, left))
        comparisons = harness.comparison_payload(
            {
                harness.CPU_CONTROL: {
                    "status": "ok",
                    "vector_sum_signature": left,
                    "hot_query_median_sec": 3.0,
                    "inclusive_wall_sec": 3.0,
                },
                harness.LEGACY: {
                    "status": "ok",
                    "vector_sum_signature": right,
                    "hot_query_median_sec": 2.0,
                    "inclusive_wall_sec": 2.0,
                },
                harness.RUNNER: {
                    "status": "ok",
                    "vector_sum_signature": left,
                    "hot_query_median_sec": 1.0,
                    "inclusive_wall_sec": 1.0,
                    "runtime_trunk_executes_end_to_end": True,
                    "internal_device_residency_between_rtdl_phases": True,
                    "hot_path_host_materialization": False,
                    "output_counts_match_requested": True,
                    "adapter_counts_present": True,
                    "output_columns_reused": True,
                },
            }
        )

        self.assertTrue(comparisons["all_variant_vector_sum_signatures_allclose"])
        self.assertFalse(comparisons["all_variant_vector_sum_signatures_hash_match"])

    def test_real_run_status_is_not_dry_run_label(self) -> None:
        args = harness.parse_args(
            [
                "--allow-non-serious-local-smoke",
                "--row-count",
                "128",
                "--group-count",
                "8",
            ]
        )
        payload = harness.build_payload(
            args=args,
            data_set={"generated_once_in_process": True},
            variant_payloads={},
            run_errors={"blocked": "no gpu"},
            selected_variants=harness.ALL_VARIANTS,
        )

        self.assertEqual(payload["summary"]["status"], harness.STATUS_RUN_FAILED_NOT_RELEASE)
        self.assertNotEqual(payload["summary"]["status"], harness.STATUS_DRY_RUN_NOT_RELEASE)


if __name__ == "__main__":
    unittest.main()
