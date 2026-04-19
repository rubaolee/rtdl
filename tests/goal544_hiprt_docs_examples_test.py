from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_hiprt_ray_triangle_hitcount.py"


class Goal544HiprtDocsExamplesTest(unittest.TestCase):
    def test_hiprt_example_runs_with_or_without_backend(self) -> None:
        env = dict(os.environ)
        env["PYTHONPATH"] = f"{ROOT / 'src'}{os.pathsep}{ROOT}"
        completed = subprocess.run(
            [sys.executable, str(EXAMPLE)],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["example"], "hiprt_ray_triangle_hitcount")
        self.assertIn("Ray3D/Triangle3D", payload["scope"])
        self.assertEqual(
            payload["cpu_python_reference"]["first_batch"],
            [
                {"ray_id": 1, "hit_count": 2},
                {"ray_id": 2, "hit_count": 0},
                {"ray_id": 3, "hit_count": 0},
            ],
        )
        self.assertEqual(
            payload["cpu_python_reference"]["second_batch"],
            [
                {"ray_id": 4, "hit_count": 2},
                {"ray_id": 5, "hit_count": 0},
            ],
        )
        if payload["hiprt_available"]:
            self.assertTrue(all(payload["parity"].values()))
            self.assertEqual(payload["run_hiprt"], payload["cpu_python_reference"]["first_batch"])
            self.assertEqual(
                payload["prepare_hiprt"]["second_batch"],
                payload["cpu_python_reference"]["second_batch"],
            )
        else:
            self.assertIn("hiprt_error", payload)


if __name__ == "__main__":
    unittest.main()
