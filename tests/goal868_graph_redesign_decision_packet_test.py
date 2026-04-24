from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal868_graph_redesign_decision_packet as goal868


ROOT = Path(__file__).resolve().parents[1]


class Goal868GraphRedesignDecisionPacketTest(unittest.TestCase):
    def test_detects_host_indexed_graph_paths(self) -> None:
        packet = goal868.build_packet(
            "static void run_bfs_expand_optix_host_indexed() {}\nstatic void run_triangle_probe_optix_host_indexed() {}\n",
            "run_bfs_expand_optix_host_indexed();\nrun_triangle_probe_optix_host_indexed();\n",
            'raise RuntimeError("graph_analytics OptiX path is host-indexed fallback today, not NVIDIA RT-core traversal")\n',
            '"graph_analytics"\nperformance_class=HOST_INDEXED_FALLBACK\nReplace host-indexed CSR helpers with a real graph-to-RT lowering or explicitly remove graph from NVIDIA RT-core app targets.\n',
        )
        self.assertEqual(packet["recommended_status"], "needs_graph_rt_redesign_or_exclusion")
        self.assertEqual(packet["current_truth"]["bfs_optix_path"], "host_indexed_correctness_path")
        self.assertEqual(packet["current_truth"]["public_app_rt_core_status"], "rejected")

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workloads_cpp = Path(tmp) / "workloads.cpp"
            api_cpp = Path(tmp) / "api.cpp"
            app_py = Path(tmp) / "app.py"
            matrix_py = Path(tmp) / "matrix.py"
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            workloads_cpp.write_text(
                "static void run_bfs_expand_optix_host_indexed() {}\nstatic void run_triangle_probe_optix_host_indexed() {}\n",
                encoding="utf-8",
            )
            api_cpp.write_text(
                "run_bfs_expand_optix_host_indexed();\nrun_triangle_probe_optix_host_indexed();\n",
                encoding="utf-8",
            )
            app_py.write_text(
                'raise RuntimeError("graph_analytics OptiX path is host-indexed fallback today, not NVIDIA RT-core traversal")\n',
                encoding="utf-8",
            )
            matrix_py.write_text(
                '"graph_analytics"\nperformance_class=HOST_INDEXED_FALLBACK\nReplace host-indexed CSR helpers with a real graph-to-RT lowering or explicitly remove graph from NVIDIA RT-core app targets.\n',
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal868_graph_redesign_decision_packet.py",
                    "--workloads-cpp",
                    str(workloads_cpp),
                    "--api-cpp",
                    str(api_cpp),
                    "--app-py",
                    str(app_py),
                    "--matrix-py",
                    str(matrix_py),
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
            self.assertEqual(payload["recommended_status"], "needs_graph_rt_redesign_or_exclusion")
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
