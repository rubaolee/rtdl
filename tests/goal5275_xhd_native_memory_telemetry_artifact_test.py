import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results"
ARTIFACTS = (
    RESULTS / "xhd_goal5275_tiny3d_native_memory_telemetry_pod_2026-07-09.json",
    RESULTS / "xhd_goal5275_stanford_sample256_native_memory_telemetry_pod_2026-07-09.json",
)


class Goal5275XhdNativeMemoryTelemetryArtifactTest(unittest.TestCase):
    def test_pod_artifacts_include_native_frontier_memory_telemetry(self):
        for path in ARTIFACTS:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                route = payload["RTDL"]["route"]["cell_mbr_summary"]["rtdl_route"]["directed_a_to_b"]
                telemetry = route["frontier_native_memory_telemetry"]
                self.assertTrue(route["frontier_native_memory_telemetry_collected"])
                self.assertEqual(
                    telemetry["schema"],
                    "rtdl.optix.cell_mbr_nearest_frontier_3d.memory_telemetry.v1",
                )
                self.assertGreater(int(telemetry["accel_output_bytes"]), 0)
                self.assertGreater(int(telemetry["accel_temp_build_bytes"]), 0)
                self.assertGreater(int(telemetry["accel_aabb_input_bytes"]), 0)
                self.assertGreater(int(telemetry["device_buffer_bytes_excluding_accel"]), 0)

    def test_memory_accounting_maps_native_accel_output_to_bvh_but_not_parity(self):
        for path in ARTIFACTS:
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                accounting = payload["RTDL"]["memory_accounting"]
                bvh = accounting["author_mapped_fields"]["BVH"]
                self.assertEqual(bvh["status"], "measured_native_optix_accel_output_buffer")
                self.assertGreater(int(bvh["bytes"]), 0)
                self.assertIn("not author Figure 11 parity", bvh["method"])
                self.assertFalse(
                    payload["RTDL"]["claim_boundary"].get("figure11_reproduction_claimed", True)
                )
                self.assertFalse(
                    payload["RTDL"]["claim_boundary"].get("author_memory_parity_claimed", True)
                )
                self.assertFalse(
                    payload["RTDL"]["claim_boundary"].get("exact_gpu_allocator_measurement_claimed", True)
                )


if __name__ == "__main__":
    unittest.main()
