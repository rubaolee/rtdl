from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "future" / "v4" / "fixed_radius_device_array_frontdoor.md"
EXAMPLE = ROOT / "future" / "v4" / "examples" / "fixed_radius_torch_device_arrays.py"


class V4FixedRadiusDocsAndExampleTest(unittest.TestCase):
    def test_doc_keeps_claim_boundaries_visible(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("not a release announcement", text)
        self.assertIn("Torch", text)
        self.assertIn("CuPy is not measured", text)
        self.assertIn("not a pure kernel-to-kernel comparison", text)
        self.assertIn("V4 release", text)
        self.assertIn("Tier-3 callback/PTX", text)
        self.assertIn("second primitive", text)

    def test_example_dry_run_is_executable_without_cuda(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(EXAMPLE), "--dry-run", "--copies", "2"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("v4_fixed_radius_torch_device_arrays", payload["example"])
        self.assertEqual(16, payload["point_count"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
