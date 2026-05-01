from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal872_native_pair_row_device_emitter_packet as goal872


ROOT = Path(__file__).resolve().parents[1]


class Goal872NativePairRowDeviceEmitterPacketTest(unittest.TestCase):
    def test_detects_device_emitter_and_boundary(self) -> None:
        packet = goal872.build_packet(
            "kSegPolyAnyhitRowsKernelSrc\natomicAdd(params.output_count, 1u)\natomicExch(params.overflowed, 1u)\nparams.output[slot] = {params.segments[sidx].id, params.polygons[prim].id}\n",
            "g_segpoly_rows.pipe = build_pipeline\noptixLaunch(g_segpoly_rows.pipe->pipeline\nstd::min<size_t>(emitted, output_capacity)\n",
            "run_seg_poly_anyhit_rows_optix_host_indexed(\n",
        )
        self.assertEqual(packet["recommended_status"], "device_emitter_implemented_pending_real_optix_gate")
        self.assertTrue(packet["evidence"]["anyhit_atomic_append_present"])
        self.assertTrue(packet["evidence"]["public_rows_path_still_host_indexed"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            core_cpp = Path(tmp) / "core.cpp"
            workloads_cpp = Path(tmp) / "workloads.cpp"
            api_cpp = Path(tmp) / "api.cpp"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            core_cpp.write_text(
                "kSegPolyAnyhitRowsKernelSrc\natomicAdd(params.output_count, 1u)\n"
                "atomicExch(params.overflowed, 1u)\n"
                "params.output[slot] = {params.segments[sidx].id, params.polygons[prim].id}\n",
                encoding="utf-8",
            )
            workloads_cpp.write_text(
                "g_segpoly_rows.pipe = build_pipeline\noptixLaunch(g_segpoly_rows.pipe->pipeline\n"
                "std::min<size_t>(emitted, output_capacity)\n",
                encoding="utf-8",
            )
            api_cpp.write_text("run_seg_poly_anyhit_rows_optix_host_indexed(\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal872_native_pair_row_device_emitter_packet.py",
                    "--core-cpp",
                    str(core_cpp),
                    "--workloads-cpp",
                    str(workloads_cpp),
                    "--api-cpp",
                    str(api_cpp),
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
            self.assertEqual(payload["recommended_status"], "device_emitter_implemented_pending_real_optix_gate")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
