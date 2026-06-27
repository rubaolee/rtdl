from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


SCRIPT = ROOT / "scripts" / "v4_goal4701_specialized_tier3_support_candidate.py"


class V4Goal4701SpecializedTier3SupportCandidateTest(unittest.TestCase):
    def test_candidate_packet_is_not_public_support(self) -> None:
        validation = v4.validate_v4_goal4701_specialized_tier3_support_candidate()
        candidate = validation["candidate"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual("specialized_numba_scalar_callback_support_candidate", candidate["candidate_label"])
        self.assertIn("Goal4700 weighted-sum app-route POD gate passed against Tier-2 denominator", candidate["evidence_chain"])
        self.assertIn(
            "20 compile/link/launch attempts across at least 4 accepted scalar callback variants",
            candidate["missing_before_public_support"],
        )
        self.assertFalse(candidate["public_support_authorized"])
        self.assertFalse(candidate["release_authorized"])
        self.assertFalse(candidate["raw_optix_callback_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "candidate.json"
            md_out = tmp_path / "candidate.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
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

        self.assertEqual("passed", payload["validation_status"])
        self.assertEqual("passed", stdout_payload["validation_status"])
        self.assertIn("not public support", markdown)


if __name__ == "__main__":
    unittest.main()
