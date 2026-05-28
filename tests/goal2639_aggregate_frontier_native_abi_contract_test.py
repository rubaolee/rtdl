from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2639_aggregate_frontier_native_abi_contract_2026-05-27.md"

sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

import rtdsl as rt


class Goal2639AggregateFrontierNativeAbiContractTest(unittest.TestCase):
    def test_native_abi_contract_is_app_independent_and_non_executable(self) -> None:
        contract = rt.validate_aggregate_frontier_collect_native_abi_contract()

        self.assertEqual(contract["primitive"], rt.AGGREGATE_FRONTIER_COLLECT_2D_PRIMITIVE)
        self.assertEqual(contract["contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT)
        self.assertEqual(contract["python_reference_contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_CONTRACT)
        self.assertFalse(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertEqual(tuple(contract["output_row_schema"]), rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA)
        self.assertEqual(contract["output_row_width"], len(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA))
        self.assertEqual(
            tuple(contract["required_native_symbols"]),
            rt.AGGREGATE_FRONTIER_COLLECT_NATIVE_REQUIRED_SYMBOLS,
        )
        self.assertIn("force_law", contract["engine_exclusions"])
        self.assertIn("app_reduction", contract["engine_exclusions"])
        self.assertNotIn("mass", json.dumps(contract["source_point_struct"]).lower())
        self.assertNotIn("mass", json.dumps(contract["tree_node_struct"]).lower())

        payload = json.dumps(contract, sort_keys=True).lower()
        for forbidden in ("barnes", "inverse-square", "collision", "contact", "dbscan"):
            self.assertNotIn(forbidden, payload)

    def test_native_abi_has_exact_fail_closed_overflow_semantics(self) -> None:
        contract = rt.validate_aggregate_frontier_collect_native_abi_contract()
        overflow_text = str(contract["overflow_semantics"])

        self.assertEqual(contract["overflow_policy"], rt.AGGREGATE_FRONTIER_COLLECT_OVERFLOW_POLICY)
        self.assertIn("emitted_count_out must be 0", overflow_text)
        self.assertIn("invalid partial workspace", overflow_text)
        self.assertIn("No partial result may be surfaced", overflow_text)
        self.assertTrue(any(str(output).startswith("attempted_count_out:") for output in contract["outputs"]))

    def test_embree_and_optix_lowering_plans_reference_abi_with_correct_maturity(self) -> None:
        embree_plan = rt.plan_aggregate_frontier_collect_lowering("embree")
        self.assertTrue(embree_plan["executable"])
        self.assertEqual(embree_plan["native_abi_contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT)
        self.assertEqual(embree_plan["native_abi_status"], "implemented_for_embree")
        self.assertEqual(embree_plan["native_output_row_width"], len(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA))
        self.assertIn("rtdl_embree_collect_aggregate_frontier_2d", embree_plan["required_native_symbol"])
        self.assertIn("optix_parity_validated", embree_plan["status"])
        self.assertIn("timing_baseline_recorded", embree_plan["status"])

        optix_plan = rt.plan_aggregate_frontier_collect_lowering("optix")
        self.assertTrue(optix_plan["executable"])
        self.assertEqual(optix_plan["native_abi_contract"], rt.AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT)
        self.assertEqual(optix_plan["native_abi_status"], "implemented_for_optix")
        self.assertEqual(optix_plan["native_output_row_width"], len(rt.AGGREGATE_FRONTIER_COLLECT_2D_ROW_SCHEMA))
        self.assertIn("rtdl_optix_collect_aggregate_frontier_2d", optix_plan["required_native_symbol"])
        self.assertIn("pod_parity_validated", optix_plan["status"])
        self.assertIn("timing_baseline_recorded", optix_plan["status"])

    def test_embree_native_symbol_matches_cpu_reference_when_available(self) -> None:
        points = tuple(
            {"id": index, "x": float(index % 8), "y": float(index // 8), "mass": 1.0}
            for index in range(32)
        )
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=4)
        expected = rt.collect_aggregate_frontier_2d(points, tree["nodes"], theta=0.5)
        try:
            actual = rt.collect_aggregate_frontier_2d_embree(
                points,
                tree["nodes"],
                theta=0.5,
                max_total_rows=expected["summary"]["frontier_row_count"],
            )
        except (RuntimeError, ValueError) as exc:
            self.skipTest(f"Embree aggregate-frontier native symbol unavailable: {exc}")

        self.assertEqual(actual["frontier_i64_rows"], expected["frontier_i64_rows"])
        self.assertEqual(actual["row_offsets"], expected["row_offsets"])
        self.assertEqual(actual["source_ids"], expected["source_ids"])
        self.assertEqual(actual["metadata"]["native_symbol"], "rtdl_embree_collect_aggregate_frontier_2d")
        self.assertFalse(actual["metadata"]["native_engine_app_specific"])

    def test_embree_native_overflow_is_fail_closed_when_available(self) -> None:
        points = tuple(
            {"id": index, "x": float(index % 4), "y": float(index // 4), "mass": 1.0}
            for index in range(16)
        )
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=2)
        try:
            with self.assertRaisesRegex(rt.AggregateFrontierOverflowError, "partial_result_returned=False"):
                rt.collect_aggregate_frontier_2d_embree(
                    points,
                    tree["nodes"],
                    theta=0.5,
                    max_total_rows=0,
                )
        except (RuntimeError, ValueError) as exc:
            self.skipTest(f"Embree aggregate-frontier native symbol unavailable: {exc}")

    def test_optix_native_symbol_matches_cpu_reference_when_available(self) -> None:
        points = tuple(
            {"id": index, "x": float(index % 8), "y": float(index // 8), "mass": 1.0}
            for index in range(32)
        )
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=4)
        expected = rt.collect_aggregate_frontier_2d(points, tree["nodes"], theta=0.5)
        try:
            actual = rt.collect_aggregate_frontier_2d_optix(
                points,
                tree["nodes"],
                theta=0.5,
                max_total_rows=expected["summary"]["frontier_row_count"],
            )
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            self.skipTest(f"OptiX aggregate-frontier native symbol unavailable: {exc}")

        self.assertEqual(actual["frontier_i64_rows"], expected["frontier_i64_rows"])
        self.assertEqual(actual["row_offsets"], expected["row_offsets"])
        self.assertEqual(actual["source_ids"], expected["source_ids"])
        self.assertEqual(actual["metadata"]["native_symbol"], "rtdl_optix_collect_aggregate_frontier_2d")
        self.assertFalse(actual["metadata"]["native_engine_app_specific"])
        self.assertIn("not an RT-core timing claim", actual["metadata"]["claim_boundary"])

    def test_optix_native_overflow_is_fail_closed_when_available(self) -> None:
        points = tuple(
            {"id": index, "x": float(index % 4), "y": float(index // 4), "mass": 1.0}
            for index in range(16)
        )
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=2)
        try:
            with self.assertRaisesRegex(rt.AggregateFrontierOverflowError, "partial_result_returned=False"):
                rt.collect_aggregate_frontier_2d_optix(
                    points,
                    tree["nodes"],
                    theta=0.5,
                    max_total_rows=0,
                )
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            self.skipTest(f"OptiX aggregate-frontier native symbol unavailable: {exc}")

    def test_report_records_no_native_or_speedup_claim(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn(rt.AGGREGATE_FRONTIER_COLLECT_2D_NATIVE_ABI_CONTRACT, text)
        self.assertIn("not RT-core speedup evidence", text)
        self.assertIn("RT-core speedup", text)
        self.assertIn("fail-closed", text)
        self.assertIn("app-name-free", text)


if __name__ == "__main__":
    unittest.main()
