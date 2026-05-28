from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
SCRIPT = ROOT / "scripts" / "goal2645_raydb_rt_perf_pod.py"


class Goal2645RayDBRtPerfRunnerTest(unittest.TestCase):
    def test_runner_dry_run_records_claim_boundary_and_matrix_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "raydb_rt_perf.json"
            output_md = Path(tmpdir) / "raydb_rt_perf.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--copies-ladder",
                    "1,10",
                    "--modes",
                    "count,sum",
                    "--backends",
                    "paper_rt_embree,paper_rt_optix",
                    "--output-json",
                    str(output_json),
                    "--output-markdown",
                    str(output_md),
                ],
                cwd=str(ROOT),
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output_json.read_text(encoding="utf-8"))

        self.assertFalse(payload["performance_claim_authorized"])
        self.assertEqual(
            payload["results"]["dry_run_matrix_shape"]["backends"],
            ["paper_rt_embree", "paper_rt_optix"],
        )
        self.assertEqual(payload["results"]["dry_run_matrix_shape"]["modes"], ["count", "sum"])
        self.assertIn("rt_core_evidence_required", payload["output_contract"])
        self.assertIn("make_build_optix_target", payload["environment"])
        self.assertIn("make_build_embree_target", payload["environment"])

    def test_runner_source_mentions_required_raydb_rt_contract(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("paper_rt_embree", source)
        self.assertIn("paper_rt_optix", source)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_primitive_grouped_i64_reduction", source)
        self.assertIn("performance_claim_authorized", source)
        self.assertIn("git_commit", source)
        self.assertIn("nvidia-smi", source)


if __name__ == "__main__":
    unittest.main()
