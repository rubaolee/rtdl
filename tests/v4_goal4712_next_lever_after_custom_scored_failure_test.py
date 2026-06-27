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

from rtdsl.v4_goal4712_next_lever_after_custom_scored_failure import (
    validate_v4_goal4712_next_lever_after_custom_scored_failure,
)


SCRIPT = ROOT / "scripts" / "v4_goal4712_next_lever_after_custom_scored_failure.py"


class V4Goal4712NextLeverAfterCustomScoredFailureTest(unittest.TestCase):
    def test_selection_rejects_polishing_failed_shape(self) -> None:
        validation = validate_v4_goal4712_next_lever_after_custom_scored_failure()
        self.assertEqual("passed", validation["status"])
        selection = validation["selection"]
        self.assertEqual("custom_predicate_early_exit_multi_hit", selection["selected_target"])
        self.assertFalse(selection["pod_authorized"])
        self.assertLess(selection["failure_fact"]["primary_geomean_v3_speedup"], 1.20)
        rejected = {row["pattern"] for row in selection["rejected_patterns"]}
        self.assertIn("post_hit_scalar_accumulation_polish", rejected)
        self.assertIn("global_atomic_scalar_accumulation", rejected)
        self.assertIn("early-exit", selection["selected_target_contract"]["generic_feature_under_test"])
        self.assertIn("materialize all", selection["selected_target_contract"]["why_this_can_win"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "goal4712.json"
            md_out = tmp_path / "goal4712.md"
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
        self.assertEqual("passed", payload["status"])
        self.assertEqual("passed", stdout_payload["status"])
        self.assertIn("Goal4712 Next Lever", markdown)


if __name__ == "__main__":
    unittest.main()
