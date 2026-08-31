from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from rtdsl.embree_same_contract_scale_probe import (
    embree_same_contract_scale_probe,
    validate_embree_same_contract_scale_probe,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_embree_same_contract_scale_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe_2026-06-11.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe_2026-06-11.json"
RAW_DIR = ROOT / "docs" / "reports" / "goal4344_embree_same_contract_scale_probe"


class Goal4344EmbreeSameContractScaleProbeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = embree_same_contract_scale_probe()

    def test_validation_accepts_five_embree_scale_artifacts(self) -> None:
        validation = validate_embree_same_contract_scale_probe()
        self.assertEqual("accept", validation["status"], validation["errors"])
        self.assertEqual(5, self.payload["summary"]["case_count"])
        self.assertEqual(5, self.payload["summary"]["embree_scale_artifact_count"])
        self.assertEqual(3, self.payload["summary"]["same_contract_query_ratio_candidate_count"])
        self.assertEqual(2, self.payload["summary"]["boundary_limited_scale_artifact_count"])
        self.assertFalse(self.payload["public_speedup_claim_authorized"])
        self.assertFalse(self.payload["release_authorized"])

    def test_raw_summary_and_artifacts_are_present(self) -> None:
        summary = json.loads((RAW_DIR / "summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["all_status_zero"])
        expected = {
            "hausdorff_embree_threshold_1024",
            "robot_embree_prepared_buffers_1024_128_4_50000",
            "contact_embree_grid64_witness128",
            "raydb_embree_count_generated_262144_1024",
            "triangle_embree_rtgraph2a1_2048",
        }
        self.assertEqual(expected, {case["name"] for case in summary["cases"]})
        for name in expected:
            self.assertTrue((RAW_DIR / f"{name}.json").exists(), name)
            self.assertEqual("", (RAW_DIR / f"{name}.stderr").read_text(encoding="utf-8"), name)
            status = json.loads((RAW_DIR / f"{name}.status.json").read_text(encoding="utf-8"))
            self.assertEqual(0, status["status"], name)

    def test_correctness_and_boundary_rows_are_explicit(self) -> None:
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "triangle_counting",
            },
            set(rows),
        )
        self.assertTrue(rows["hausdorff_xhd"]["correctness"]["oracle_decision_matches"])
        self.assertTrue(rows["contact_manifold"]["correctness"]["matches_cpu_reference"])
        self.assertTrue(rows["contact_manifold"]["correctness"]["complete_candidate_coverage"])
        self.assertTrue(rows["raydb_style"]["correctness"]["matches_cpu_reference"])
        self.assertTrue(rows["triangle_counting"]["correctness"]["triangle_count_matches_oracle"])

        self.assertEqual(
            "same_scene_query_scale_output_residency_boundary",
            rows["robot_collision"]["comparison_class"],
        )
        self.assertEqual(
            "same_scale_prepared_residency_boundary",
            rows["raydb_style"]["comparison_class"],
        )
        self.assertFalse(rows["robot_collision"]["clean_end_to_end_ratio_authorized"])
        self.assertFalse(rows["raydb_style"]["clean_end_to_end_ratio_authorized"])

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "probe.json"
            out_md = Path(tmp) / "probe.md"
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
            self.assertIn("Goal4344", report)
            self.assertIn("boundary-limited", report)
            self.assertIn("robot_collision", report)

    def test_committed_report_and_json_artifact_are_present(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        payload = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertIn("Embree Same-Contract Scale Probe", text)
        self.assertIn("same_contract_query_ratio_candidate", text)
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertEqual(5, payload["summary"]["case_count"])


if __name__ == "__main__":
    unittest.main()
