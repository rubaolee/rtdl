from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.cpu_only_pod_comparison_launch import (
    cpu_only_pod_comparison_launch_packet,
    validate_cpu_only_pod_comparison_launch_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_cpu_only_pod_comparison_launch.py"
REPORT = ROOT / "docs" / "reports" / "goal4346_cpu_only_pod_comparison_launch_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4346_cpu_only_pod_comparison_launch_2026-06-11.json"


class Goal4346CpuOnlyPodComparisonLaunchTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = cpu_only_pod_comparison_launch_packet()

    def test_validation_accepts_cpu_only_launch_packet(self) -> None:
        validation = validate_cpu_only_pod_comparison_launch_packet()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual("nvidia_rt_core_optix_vs_embree_cpu_only", self.payload["target"])
        self.assertEqual("omitted_by_user_until_hardware_exists", self.payload["intel_gpu_lane"])
        self.assertFalse(self.payload["requires"]["intel_gpu"])
        self.assertTrue(self.payload["requires"]["nvidia_rt_core_pod_for_optix"])
        self.assertTrue(self.payload["requires"]["reject_non_rt_core_nvidia_gpus_for_rt_core_timing"])
        self.assertTrue(self.payload["requires"]["cuda_12_8_ptxas_first_for_numba_rows"])

    def test_environment_prefix_pins_working_numba_cuda_toolchain(self) -> None:
        env_lines = tuple(self.payload["environment_prefix"])
        env_text = "\n".join(env_lines)
        self.assertIn("RTDL_CUDA_PREFIX=${RTDL_CUDA_PREFIX:-/usr/local/cuda-12.8}", env_text)
        self.assertIn("NUMBA_CUDA_PREFIX=${NUMBA_CUDA_PREFIX:-/usr/local/lib/python3.12/dist-packages/nvidia/cuda_nvcc}", env_text)
        self.assertIn("CUDA_HOME=$NUMBA_CUDA_PREFIX", env_text)
        self.assertIn("CUDA_PATH=$NUMBA_CUDA_PREFIX", env_text)
        self.assertIn("PATH=$RTDL_CUDA_PREFIX/bin:$NUMBA_CUDA_PREFIX/bin:$PATH", env_text)
        self.assertIn("$NUMBA_CUDA_PREFIX/nvvm/lib64", env_text)

    def test_embree_cpu_commands_cover_ready_cpu_rows_only(self) -> None:
        rows = {row["app"]: row for row in self.payload["embree_cpu_scale_commands"]}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "librts_spatial_index",
                "triangle_counting",
            },
            set(rows),
        )
        for app, row in rows.items():
            text = " ".join(row["command"]).lower()
            self.assertIn("embree", text, app)
            self.assertNotIn("intel", text, app)
            self.assertFalse(row["requires_intel_gpu"], app)
            self.assertFalse(row["public_speedup_claim_authorized"], app)
        self.assertEqual("fully_optimized_measured_pair", rows["librts_spatial_index"]["bucket"])
        self.assertEqual("clean_internal_query_ratio", rows["raydb_style"]["bucket"])
        self.assertIn("Goal4364", rows["raydb_style"]["note"])

    def test_contract_choice_blockers_remain_explicit(self) -> None:
        blockers = {row["app"]: row for row in self.payload["contract_choice_blockers"]}
        self.assertEqual({}, blockers)
        self.assertEqual(0, self.payload["current_comparison_summary"]["contract_choice_blocker_count"])

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "launch.json"
            out_md = Path(tmp) / "launch.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("CPU-Only Pod Comparison Launch", report)
            self.assertIn("No Intel-GPU lane", report)
            self.assertIn("Do not use Pascal/GTX hardware", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("CPU-Only Pod Comparison Launch", text)
        self.assertIn("NVIDIA RT-core OptiX versus Embree CPU only", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertFalse(payload["requires"]["intel_gpu"])


if __name__ == "__main__":
    unittest.main()
