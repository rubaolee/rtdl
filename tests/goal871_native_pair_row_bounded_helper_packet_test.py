from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal871_native_pair_row_bounded_helper_packet as goal871


ROOT = Path(__file__).resolve().parents[1]


class Goal871NativePairRowBoundedHelperPacketTest(unittest.TestCase):
    def test_detects_helper_and_empty_success_boundary(self) -> None:
        helper = "run_seg_poly_anyhit_rows_optix_native_bounded"
        packet = goal871.build_packet(
            f"{helper}(\nrun_seg_poly_anyhit_rows_optix_host_indexed(\n",
            f"static void {helper}(\n*emitted_count_out = 0;\n*overflowed_out = 0;\nif (segment_count == 0 || polygon_count == 0) {{\nreturn;\n}}\nOptiX pair-row emission is still pending\n",
        )
        self.assertEqual(packet["recommended_status"], "bounded_helper_added")
        self.assertTrue(packet["evidence"]["helper_present"])
        self.assertTrue(packet["evidence"]["empty_input_success_path_present"])
        self.assertEqual(packet["current_behavior"]["non_empty_input"], "explicit_not_implemented_until_native_emitter_exists")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            api_cpp = Path(tmp) / "api.cpp"
            workloads_cpp = Path(tmp) / "workloads.cpp"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            helper = "run_seg_poly_anyhit_rows_optix_native_bounded"
            api_cpp.write_text(
                f"{helper}(\nrun_seg_poly_anyhit_rows_optix_host_indexed(\n",
                encoding="utf-8",
            )
            workloads_cpp.write_text(
                f"static void {helper}(\n*emitted_count_out = 0;\n*overflowed_out = 0;\n"
                "if (segment_count == 0 || polygon_count == 0) {\nreturn;\n}\n"
                "OptiX pair-row emission is still pending\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal871_native_pair_row_bounded_helper_packet.py",
                    "--api-cpp",
                    str(api_cpp),
                    "--workloads-cpp",
                    str(workloads_cpp),
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
            self.assertEqual(payload["recommended_status"], "bounded_helper_added")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
