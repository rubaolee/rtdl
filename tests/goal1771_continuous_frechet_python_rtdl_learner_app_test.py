from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_continuous_frechet_distance_app.py"


def run_example(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(EXAMPLE), *args],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal1771ContinuousFrechetPythonRtdlLearnerAppTest(unittest.TestCase):
    def test_cpu_reference_continuous_frechet_distance_matches_oracle(self) -> None:
        payload = run_example("--backend", "cpu_python_reference", "--iterations", "18")
        self.assertEqual(payload["app"], "continuous_frechet_distance")
        self.assertEqual(payload["candidate_mode"], "all_cells")
        self.assertTrue(payload["matches_oracle"])
        self.assertGreater(float(payload["distance_estimate"]), 0.0)
        self.assertIn("continuous Frechet free-space", payload["rtdl_role"])
        self.assertFalse(payload["rt_core_accelerated"])

    def test_rtdl_broadphase_keeps_python_owned_exact_frechet_boundary(self) -> None:
        payload = run_example(
            "--backend",
            "cpu_python_reference",
            "--candidate-mode",
            "rtdl_broadphase",
            "--iterations",
            "18",
            "--decision-radius",
            "0.25",
        )
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["decision"]["within_radius"], True)  # type: ignore[index]
        self.assertGreater(payload["decision"]["candidate_cell_count"], 0)  # type: ignore[index]
        self.assertIn("Python owns the continuous Frechet", payload["rtdl_role"])
        self.assertIn("not a universal speedup claim", payload["claim_boundary"])

    def test_require_rt_core_is_reserved_for_optix_broadphase(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--candidate-mode",
                "rtdl_broadphase",
                "--require-rt-core",
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": "src:."},
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("--require-rt-core is only meaningful with --backend optix", completed.stderr)

    def test_source_mentions_native_optix_rt_core_path_without_overclaiming(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")
        self.assertIn("segment_polygon_anyhit_rows_native_bounded_optix", text)
        self.assertIn("exact free-space dynamic program remains Python-owned", text)
        self.assertIn("not a universal speedup claim", text)


if __name__ == "__main__":
    unittest.main()
