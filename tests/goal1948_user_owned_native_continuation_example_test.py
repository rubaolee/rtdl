from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "rtdl_hausdorff_user_cpp_continuation.py"
REPORT = ROOT / "docs" / "reports" / "goal1948_user_owned_native_continuation_example_2026-05-13.md"


class Goal1948UserOwnedNativeContinuationExampleTest(unittest.TestCase):
    def test_example_static_boundaries_are_explicit(self) -> None:
        text = EXAMPLE.read_text(encoding="utf-8")

        self.assertIn("CPP_CONTINUATION_SOURCE", text)
        self.assertIn("learner_owned_cpp", text)
        self.assertIn("counts_as_v2_partner_speedup", text)
        self.assertIn("False", text)
        self.assertIn("not an official Torch/CuPy v2 partner claim", text)

    def test_example_python_continuation_executes_and_matches_oracle(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(EXAMPLE),
                "--backend",
                "cpu_python_reference",
                "--continuation",
                "python",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["app"], "hausdorff_user_cpp_continuation")
        self.assertEqual(payload["continuation"], "python_reference")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["witness_direction"], payload["oracle"]["witness_direction"])
        self.assertFalse(payload["counts_as_v2_partner_speedup"])
        self.assertEqual(payload["rows_a_to_b"], 4)
        self.assertEqual(payload["rows_b_to_a"], 4)

    def test_report_documents_user_owned_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("RTDL generic k=1 nearest-neighbor rows", text)
        self.assertIn("learner-owned C++", text)
        self.assertIn("does not count as a v2.0 partner speedup row", text)
        self.assertIn("RTDL Python apps can interoperate with user-owned C/C++ continuations", text)
        self.assertIn("official v2.0 partner acceleration path", text)
        self.assertIn("192.168.1.20", text)
        self.assertIn("/usr/bin/g++", text)
        self.assertIn("witness direction", text)
        self.assertIn("exact ties choose `b_to_a`", text)


if __name__ == "__main__":
    unittest.main()
