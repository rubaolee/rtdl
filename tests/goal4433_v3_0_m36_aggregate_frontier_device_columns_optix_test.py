from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
REPORT = ROOT / "docs/reports/goal4433_v3_0_m36_aggregate_frontier_device_columns_optix_2026-06-16.md"

sys.path.insert(0, str(ROOT / "src"))


def _has_cupy() -> bool:
    try:
        import cupy  # noqa: F401
    except Exception:
        return False
    return True


class Goal4433V30M36AggregateFrontierDeviceColumnsOptixTest(unittest.TestCase):
    def test_native_symbols_are_declared(self) -> None:
        prelude = PRELUDE.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        for symbol in (
            "rtdl_optix_prepare_aggregate_frontier_device_columns_2d",
            "rtdl_optix_run_aggregate_frontier_device_columns_2d",
            "rtdl_optix_destroy_aggregate_frontier_device_columns_2d",
        ):
            self.assertIn(symbol, prelude)
            self.assertIn(symbol, api)
        self.assertIn("struct RtdlAggregateFrontierDeviceColumns2D", prelude)
        self.assertIn("rtdl_aggregate_frontier_count_2d", api)
        self.assertIn("rtdl_aggregate_frontier_prefix_2d", api)
        self.assertIn("rtdl_aggregate_frontier_write_2d", api)

    def test_new_device_column_body_does_not_wrap_old_host_row_collector(self) -> None:
        api = API.read_text(encoding="utf-8")
        start = api.index("struct AggregateFrontierDeviceNode2D")
        end = api.index("struct CollectKStageProfile")
        body = api[start:end]
        self.assertNotIn("rtdl_optix_collect_aggregate_frontier_2d(", body)
        self.assertNotIn("std::vector<int64_t> frontier_rows", body)
        self.assertIn("cuLaunchKernel", body)
        self.assertIn("row_offsets", body)
        self.assertIn("source_ids_device_ptr", body)

    def test_python_wrapper_and_contract_are_exported(self) -> None:
        import rtdsl as rt

        contract = rt.validate_aggregate_frontier_device_columns_native_abi_contract()
        self.assertEqual(contract["status"], "implemented_optix_device_columns")
        self.assertTrue(contract["executable"])
        self.assertTrue(contract["app_generic"])
        self.assertTrue(contract["claim_boundary"]["implementation_claim_authorized"])
        self.assertFalse(contract["claim_boundary"]["rt_core_speedup_claim_authorized"])
        self.assertTrue(hasattr(rt, "prepare_aggregate_frontier_device_columns_2d_optix"))
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("OptixAggregateFrontierDeviceColumns2DOutput", runtime)
        self.assertIn("frontier_columns_materialized_on_host", runtime)
        self.assertIn("False", runtime)

    @unittest.skipUnless(_has_cupy(), "CuPy is required for device-pointer runtime parity")
    def test_runtime_device_columns_match_cpu_reference_when_optix_is_available(self) -> None:
        import cupy as cp
        import rtdsl as rt

        points = [
            rt.WeightedPointRow(i, float(i % 8), float((i * 5) % 11), 1.0)
            for i in range(64)
        ]
        tree = rt.build_bucketized_aggregate_tree_2d(points, bucket_size=4)
        expected = rt.collect_aggregate_frontier_2d(points, tree["nodes"], theta=0.5)
        try:
            prepared = rt.prepare_aggregate_frontier_device_columns_2d_optix(
                tree["nodes"],
                theta=0.5,
            )
        except Exception as exc:
            self.skipTest(f"OptiX aggregate-frontier device-column backend unavailable: {exc}")

        with prepared:
            actual = prepared.run_cupy(points, row_capacity=len(expected["frontier_i64_rows"]) + 32)
            self.assertFalse(actual.overflow)
            self.assertTrue(actual.device_resident)
            columns = actual.as_cupy_columns()
            materialized = tuple(
                zip(
                    *(tuple(int(v) for v in cp.asnumpy(columns[name]).tolist()) for name in actual.row_schema)
                )
            )
            row_offsets = tuple(int(v) for v in cp.asnumpy(columns["row_offsets"]).tolist())
            self.assertEqual(materialized, expected["frontier_i64_rows"])
            self.assertEqual(row_offsets, expected["row_offsets"])
            metadata = actual.to_metadata()
            self.assertFalse(metadata["frontier_columns_materialized_on_host"])
            self.assertFalse(metadata["row_offsets_materialized_on_host"])
            self.assertEqual(metadata["native_symbol"], "rtdl_optix_run_aggregate_frontier_device_columns_2d")

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "implemented_optix_device_columns",
            "device-resident columns",
            "does not wrap the old host-row collector",
            "speedup claim remains unauthorized",
            "valid until the prepared handle is run again or closed",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
