from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_tier3_numba_ptx_probe.py"
DOC = ROOT / "future" / "v4" / "tier3_numba_ptx_spike.md"


class V4Tier3NumbaPtxProbeTest(unittest.TestCase):
    def test_dry_run_does_not_authorize_tier3_support(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "tier3.json"
            md_out = tmp_path / "tier3.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("dry_run", stdout_payload["status"])
        self.assertFalse(payload["ptx_generated"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertFalse(payload["raw_optix_callback_claim_authorized"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertIn("not Tier-3 support", markdown)

    def test_doc_states_spike_boundary(self) -> None:
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Only step 2 is probed here", text)
        self.assertIn("does not mean that OptiX accepts the PTX", text)
        self.assertIn("Tier-3 callback/PTX support claims", text)


if __name__ == "__main__":
    unittest.main()

