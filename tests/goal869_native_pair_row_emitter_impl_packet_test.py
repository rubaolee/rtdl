from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal869_native_pair_row_emitter_impl_packet as goal869


ROOT = Path(__file__).resolve().parents[1]


class Goal869NativePairRowEmitterImplPacketTest(unittest.TestCase):
    def test_detects_foundation_and_missing_variable_output_path(self) -> None:
        packet = goal869.build_packet(
            "kSegPolyHitcountKernelSrc\n__raygen__segpoly_probe\nGpuSegPolyRecord* output;\nsizeof(GpuSegPolyRecord) * segment_count\n",
            "rtdl_optix_run_segment_polygon_anyhit_rows(\nrun_seg_poly_anyhit_rows_optix_host_indexed(\n",
            "rtdl_optix_run_segment_polygon_anyhit_rows(\n",
        )
        self.assertEqual(packet["current_truth"]["native_hitcount_foundation"], "present")
        self.assertEqual(packet["current_truth"]["existing_native_output_shape"], "fixed_one_row_per_segment")
        self.assertEqual(packet["current_truth"]["public_rows_execution"], "host_indexed")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workloads_cpp = Path(tmp) / "workloads.cpp"
            api_cpp = Path(tmp) / "api.cpp"
            prelude_h = Path(tmp) / "prelude.h"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            workloads_cpp.write_text(
                "kSegPolyHitcountKernelSrc\n__raygen__segpoly_probe\nGpuSegPolyRecord* output;\nsizeof(GpuSegPolyRecord) * segment_count\n",
                encoding="utf-8",
            )
            api_cpp.write_text(
                "rtdl_optix_run_segment_polygon_anyhit_rows(\nrun_seg_poly_anyhit_rows_optix_host_indexed(\n",
                encoding="utf-8",
            )
            prelude_h.write_text(
                "rtdl_optix_run_segment_polygon_anyhit_rows(\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal869_native_pair_row_emitter_impl_packet.py",
                    "--workloads-cpp",
                    str(workloads_cpp),
                    "--api-cpp",
                    str(api_cpp),
                    "--prelude-h",
                    str(prelude_h),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                env={**os.environ, "PYTHONPATH": "src:."},
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["recommended_status"], "implementation_packet_ready")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
