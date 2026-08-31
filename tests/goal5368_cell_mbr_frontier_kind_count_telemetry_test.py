import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"


class Goal5368CellMbrFrontierKindCountTelemetryTest(unittest.TestCase):
    def test_native_tracks_raw_frontier_kind_counts_before_row_download(self):
        text = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn("raw_frontier_kind_counts", text)
        self.assertIn("g_optix_last_cell_mbr_frontier_raw_kind1_rows", text)
        self.assertIn("g_optix_last_cell_mbr_frontier_raw_kind2_rows", text)
        self.assertIn("g_optix_last_cell_mbr_frontier_raw_kind3_rows", text)
        self.assertIn("atomicAdd(&params.raw_frontier_kind_counts[(uint32_t)kind], 1ULL)", text)
        self.assertIn("download(raw_kind_counts, d_raw_frontier_kind_counts.ptr, 4)", text)
        self.assertLess(
            text.index("download(raw_kind_counts, d_raw_frontier_kind_counts.ptr, 4)"),
            text.index("if (raw_count > row_capacity)"),
        )

    def test_native_exposes_memory_telemetry_v3_without_app_identity(self):
        prelude = PRELUDE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        self.assertIn(
            "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3",
            prelude,
        )
        self.assertIn(
            "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3",
            workloads,
        )
        v3_start = workloads.index(
            "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3"
        )
        v3_block = workloads[v3_start : v3_start + 2500]
        self.assertIn("raw_frontier_kind1_rows", v3_block)
        self.assertIn("raw_frontier_kind2_rows", v3_block)
        self.assertIn("raw_frontier_kind3_rows", v3_block)
        for forbidden in ("xhd", "X-HD", "hausdorff", "author", "paper"):
            self.assertNotIn(forbidden, v3_block)

    def test_python_runtime_prefers_v3_and_can_return_overflow_telemetry_only(self):
        text = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("allow_overflow_telemetry: bool = False", text)
        self.assertIn(
            "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry_v3",
            text,
        )
        self.assertIn(
            "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v3",
            text,
        )
        self.assertIn('"raw_frontier_kind_counts"', text)
        self.assertIn('"raw_frontier_kind2_rows"', text)
        self.assertIn('"overflow_telemetry_only": True', text)
        self.assertIn('"overflow_failure_mode": "fail_closed_overflow_no_rows_returned"', text)


if __name__ == "__main__":
    unittest.main()
