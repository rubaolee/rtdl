import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
MEMORY_HELPER = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "xhd_memory_accounting.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
PARTNER_CONTINUATIONS = ROOT / "src" / "rtdsl" / "partner_continuations.py"
ROUTE_GATE = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_cell_mbr_frontier_route_gate.py"


def _load_memory_helper():
    spec = importlib.util.spec_from_file_location("xhd_memory_accounting_goal5275", MEMORY_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {MEMORY_HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5275XhdNativeMemoryTelemetryContractTest(unittest.TestCase):
    def test_memory_helper_maps_native_accel_output_to_bvh_when_present(self):
        helper = _load_memory_helper()
        payload = {
            "RTDL": {
                "route_label": "cell-mbr-fast-scalar",
                "point_count_a": 3,
                "point_count_b": 5,
                "route": {
                    "directed_a_to_b": {
                        "grid_cell_count": 2,
                        "frontier_row_capacity": 7,
                        "frontier_row_count": 4,
                        "frontier_native_memory_telemetry": {
                            "accel_output_bytes": 4096,
                            "accel_temp_build_bytes": 8192,
                            "accel_aabb_input_bytes": 128,
                            "device_buffer_bytes_excluding_accel": 2048,
                        },
                        "initial_native_phase_timings": {
                            "point_row_index_count": 5,
                            "dense_cell_position_count": 8,
                        },
                    },
                    "route_contract": "test",
                },
            }
        }

        accounting = helper.rtdl_memory_accounting_from_hd_exec_payload(payload)
        self.assertEqual(
            accounting["author_mapped_fields"]["BVH"]["status"],
            "measured_native_optix_accel_output_buffer",
        )
        self.assertEqual(accounting["author_mapped_fields"]["BVH"]["bytes"], 4096)
        self.assertEqual(
            accounting["rtdl_only_fields"]["native_accel_build_temp"]["bytes"],
            8192,
        )
        self.assertEqual(
            accounting["rtdl_only_fields"]["native_accel_aabb_input"]["bytes"],
            128,
        )
        self.assertEqual(
            accounting["rtdl_only_fields"]["native_route_device_buffers_excluding_accel"]["bytes"],
            2048,
        )

    def test_native_optional_memory_symbol_is_declared_and_exposed_to_python(self):
        symbol = "rtdl_optix_cell_mbr_nearest_frontier_3d_get_last_memory_telemetry"
        self.assertIn(symbol, OPTIX_WORKLOADS.read_text(encoding="utf-8"))
        self.assertIn(symbol, OPTIX_PRELUDE.read_text(encoding="utf-8"))
        runtime_text = OPTIX_RUNTIME.read_text(encoding="utf-8")
        self.assertIn(symbol, runtime_text)
        self.assertIn("native_memory_telemetry", runtime_text)
        self.assertIn("accel_output_bytes", runtime_text)

    def test_accel_holder_tracks_output_temp_and_aabb_sizes(self):
        text = OPTIX_CORE.read_text(encoding="utf-8")
        self.assertIn("output_size_bytes", text)
        self.assertIn("temp_size_bytes", text)
        self.assertIn("aabb_size_bytes", text)
        self.assertIn("compacted_output_size_bytes", text)

    def test_route_summary_forwards_native_memory_telemetry(self):
        partner_text = PARTNER_CONTINUATIONS.read_text(encoding="utf-8")
        self.assertIn('"native_memory_telemetry_collected"', partner_text)
        self.assertIn('"native_memory_telemetry"', partner_text)
        text = ROUTE_GATE.read_text(encoding="utf-8")
        self.assertIn("frontier_native_memory_telemetry_collected", text)
        self.assertIn("frontier_native_memory_telemetry", text)


if __name__ == "__main__":
    unittest.main()
