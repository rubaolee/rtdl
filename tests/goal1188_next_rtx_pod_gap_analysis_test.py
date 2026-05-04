from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1188_next_rtx_pod_gap_analysis as goal1188


ROOT = Path(__file__).resolve().parents[1]


class Goal1188NextRtxPodGapAnalysisTest(unittest.TestCase):
    def test_current_gap_analysis_is_valid(self) -> None:
        payload = goal1188.build_analysis()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["reviewed_public_wording_count"], 12)
        self.assertEqual(payload["needs_public_wording_evidence_count"], 2)
        self.assertEqual(payload["blocked_public_wording_count"], 2)

    def test_expected_apps_need_public_wording_evidence(self) -> None:
        payload = goal1188.build_analysis()
        self.assertEqual(
            set(payload["needs_public_wording_apps"]),
            {
                "database_analytics",
                "polygon_set_jaccard",
            },
        )
        for row in payload["rows"]:
            if row["app"] in payload["needs_public_wording_apps"]:
                self.assertEqual(row["bucket"], "needs_public_wording_evidence")
                self.assertTrue(row["next_local"])
                self.assertTrue(row["next_pod"])

    def test_timing_only_followups_remain_non_promotion(self) -> None:
        payload = goal1188.build_analysis()
        followups = payload["timing_only_followups"]
        self.assertIn("ann_candidate_search", followups)
        self.assertIn("robot_collision_screening", followups)
        self.assertIn("timing-only", followups["ann_candidate_search"]["status"])
        self.assertIn("timing-only", followups["robot_collision_screening"]["status"])
        self.assertIn("do not promote", followups["ann_candidate_search"]["next_action"])
        self.assertIn("do not promote", followups["robot_collision_screening"]["next_action"])

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "analysis.json"
            output_md = Path(tmp) / "analysis.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1188_next_rtx_pod_gap_analysis.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("Goal1188 Next RTX Pod Gap Analysis", markdown)
            self.assertIn("Do not spend another pod session", markdown)
            self.assertIn("apps needing public-wording evidence: `2`", markdown)


if __name__ == "__main__":
    unittest.main()
