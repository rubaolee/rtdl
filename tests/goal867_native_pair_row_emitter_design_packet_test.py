from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal867_native_pair_row_emitter_design_packet as goal867


ROOT = Path(__file__).resolve().parents[1]


class Goal867NativePairRowEmitterDesignPacketTest(unittest.TestCase):
    def test_current_truth_detects_host_indexed_gap(self) -> None:
        packet = goal867.build_packet(
            "extern \"C\" int rtdl_optix_run_segment_polygon_anyhit_rows(){ run_seg_poly_anyhit_rows_optix_host_indexed(); }",
            "static void run_seg_poly_anyhit_rows_optix_host_indexed() {}",
            "__raygen__rtdl_segment_polygon_anyhit_rows_probe\n// Goal 126 placeholder:\n__closesthit__rtdl_segment_polygon_anyhit_rows_refine\n// Materialize one (segment_id, polygon_id) row",
        )
        self.assertEqual(packet["recommended_status"], "needs_native_pair_row_emitter_implementation")
        self.assertEqual(packet["current_truth"]["runtime_execution"], "host_indexed_exact_cpu_loop")
        self.assertEqual(packet["current_truth"]["device_codegen"], "placeholder_only")

    def test_ready_state_requires_non_placeholder_and_non_host_indexed(self) -> None:
        packet = goal867.build_packet(
            "extern \"C\" int rtdl_optix_run_segment_polygon_anyhit_rows(){ run_seg_poly_anyhit_rows_optix_native(); }",
            "static void run_seg_poly_anyhit_rows_optix_native() {}",
            "__raygen__rtdl_segment_polygon_anyhit_rows_probe\nextern \"C\" __global__ void __closesthit__rtdl_segment_polygon_anyhit_rows_refine() {}",
        )
        self.assertEqual(packet["recommended_status"], "ready_for_native_pair_row_gate")
        self.assertEqual(packet["blocker"], "none")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            api_cpp = Path(tmp) / "api.cpp"
            workloads_cpp = Path(tmp) / "workloads.cpp"
            codegen_py = Path(tmp) / "codegen.py"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            api_cpp.write_text(
                "extern \"C\" int rtdl_optix_run_segment_polygon_anyhit_rows(){ run_seg_poly_anyhit_rows_optix_host_indexed(); }\n",
                encoding="utf-8",
            )
            workloads_cpp.write_text(
                "static void run_seg_poly_anyhit_rows_optix_host_indexed() {}\n",
                encoding="utf-8",
            )
            codegen_py.write_text(
                "__raygen__rtdl_segment_polygon_anyhit_rows_probe\n// Goal 126 placeholder:\n"
                "__closesthit__rtdl_segment_polygon_anyhit_rows_refine\n// Materialize one (segment_id, polygon_id) row\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal867_native_pair_row_emitter_design_packet.py",
                    "--api-cpp",
                    str(api_cpp),
                    "--workloads-cpp",
                    str(workloads_cpp),
                    "--codegen-py",
                    str(codegen_py),
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
            self.assertEqual(payload["recommended_status"], "needs_native_pair_row_emitter_implementation")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
