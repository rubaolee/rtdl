from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal870_native_pair_row_emitter_abi_packet as goal870


ROOT = Path(__file__).resolve().parents[1]


class Goal870NativePairRowEmitterAbiPacketTest(unittest.TestCase):
    def test_detects_scaffold_and_non_promotion(self) -> None:
        symbol = "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded"
        packet = goal870.build_packet(
            f"{symbol}(\n",
            f"{symbol}(\nsize_t output_capacity\nsize_t* emitted_count_out\nuint32_t* overflowed_out\nnative bounded segment_polygon_anyhit_rows emitter is not implemented yet\nrun_seg_poly_anyhit_rows_optix_host_indexed(\n",
        )
        self.assertTrue(packet["evidence"]["declaration_present"])
        self.assertTrue(packet["evidence"]["definition_present"])
        self.assertTrue(packet["evidence"]["public_rows_path_still_host_indexed"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prelude_h = Path(tmp) / "prelude.h"
            api_cpp = Path(tmp) / "api.cpp"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            symbol = "rtdl_optix_run_segment_polygon_anyhit_rows_native_bounded"
            prelude_h.write_text(f"{symbol}(\n", encoding="utf-8")
            api_cpp.write_text(
                f"{symbol}(\nsize_t output_capacity\nsize_t* emitted_count_out\nuint32_t* overflowed_out\n"
                "native bounded segment_polygon_anyhit_rows emitter is not implemented yet\n"
                "run_seg_poly_anyhit_rows_optix_host_indexed(\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal870_native_pair_row_emitter_abi_packet.py",
                    "--prelude-h",
                    str(prelude_h),
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
            self.assertEqual(payload["recommended_status"], "abi_scaffold_added")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
