from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal5281NativeHeavyOffloadTelemetryContractTest(unittest.TestCase):
    def test_native_v2_memory_symbol_is_declared_and_exposed(self) -> None:
        symbol = "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v2"
        self.assertIn(symbol, OPTIX_WORKLOADS.read_text(encoding="utf-8"))
        self.assertIn(symbol, OPTIX_PRELUDE.read_text(encoding="utf-8"))
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn(symbol, runtime)
        self.assertIn("rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v2", runtime)

    def test_native_records_generic_heavy_offload_peak_fields(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        for token in (
            "g_optix_last_cell_mbr_frontier_in_queue_capacity",
            "g_optix_last_cell_mbr_frontier_miss_queue_capacity",
            "g_optix_last_cell_mbr_frontier_heavy_offload_row_capacity",
            "g_optix_last_cell_mbr_frontier_heavy_offload_current_rows",
            "g_optix_last_cell_mbr_frontier_heavy_offload_peak_rows",
            "g_optix_last_cell_mbr_frontier_heavy_offload_queue_current_bytes",
            "g_optix_last_cell_mbr_frontier_heavy_offload_queue_peak_bytes",
        ):
            self.assertIn(token, workloads)
        self.assertIn("row.frontier_kind_code == 2", workloads)
        self.assertIn("offload_row_count * 2ULL", workloads)

    def test_python_telemetry_keeps_boundary_language(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        for key in (
            '"in_queue_capacity"',
            '"miss_queue_capacity"',
            '"heavy_offload_row_capacity"',
            '"heavy_offload_current_rows"',
            '"heavy_offload_peak_rows"',
            '"heavy_offload_queue_current_bytes"',
            '"heavy_offload_queue_peak_bytes"',
        ):
            self.assertIn(key, runtime)
        self.assertIn("not author Figure 11 parity", runtime)
        self.assertIn("author Figure 11 parity claim", runtime)


if __name__ == "__main__":
    unittest.main()
