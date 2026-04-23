from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal836RtxBaselineReadinessGateTest(unittest.TestCase):
    def test_two_ai_consensus_artifacts_exist(self) -> None:
        ledger = ROOT / "docs" / "reports" / "goal836_two_ai_consensus_2026-04-23.md"
        codex = ROOT / "docs" / "reports" / "goal836_codex_consensus_review_2026-04-23.md"
        gemini = ROOT / "docs" / "reports" / "goal836_gemini_external_consensus_review_2026-04-23.md"

        for path in (ledger, codex, gemini):
            self.assertTrue(path.exists(), str(path))

        ledger_text = ledger.read_text(encoding="utf-8")
        self.assertIn("Codex: ACCEPT", ledger_text)
        self.assertIn("Gemini 2.5 Flash: ACCEPT", ledger_text)
        self.assertIn("No Claude verdict is claimed", ledger_text)

    def test_real_plan_currently_needs_baselines_without_running_cloud(self) -> None:
        module = __import__("scripts.goal836_rtx_baseline_readiness_gate", fromlist=["analyze_plan", "to_markdown"])
        payload = module.analyze_plan()
        self.assertEqual(payload["status"], "needs_baselines")
        self.assertGreater(payload["required_artifact_count"], 0)
        self.assertGreater(payload["missing_artifact_count"], 0)
        self.assertIn("does not run benchmarks", payload["boundary"])
        markdown = module.to_markdown(payload)
        self.assertIn("An RTX speedup claim package is incomplete", markdown)

    def test_synthetic_valid_artifact_passes_schema(self) -> None:
        module = __import__(
            "scripts.goal836_rtx_baseline_readiness_gate",
            fromlist=["analyze_plan", "expected_artifact_path"],
        )
        plan = {
            "goal": "synthetic",
            "rows": [
                {
                    "section": "active",
                    "app": "demo_app",
                    "path_name": "demo_path",
                    "baseline_artifact_stub": "docs/reports/goal835_baseline_demo_app_demo_path_<backend>_2026-04-23.json",
                    "required_baselines": ["cpu_oracle"],
                    "required_phases": ["build", "query", "copyback"],
                    "minimum_repeated_runs": 3,
                    "comparable_metric_scope": "same synthetic compact summary",
                    "scale": {"copies": 7, "iterations": 3},
                    "claim_limit": "synthetic only",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_root = Path(tmpdir)
            row = plan["rows"][0]
            path = module.expected_artifact_path(row, "cpu_oracle", artifact_root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "app": "demo_app",
                        "path_name": "demo_path",
                        "baseline_name": "cpu_oracle",
                        "status": "ok",
                        "correctness_parity": True,
                        "phase_separated": True,
                        "authorizes_public_speedup_claim": False,
                        "repeated_runs": 3,
                        "required_phase_coverage": ["build", "query", "copyback"],
                        "comparable_metric_scope": "same synthetic compact summary",
                        "benchmark_scale": {"copies": 7, "iterations": 3},
                    }
                ),
                encoding="utf-8",
            )
            payload = module.analyze_plan(plan, artifact_root)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["valid_artifact_count"], 1)
            self.assertEqual(payload["missing_artifact_count"], 0)
            self.assertEqual(payload["invalid_artifact_count"], 0)

    def test_synthetic_invalid_artifact_reports_schema_errors(self) -> None:
        module = __import__(
            "scripts.goal836_rtx_baseline_readiness_gate",
            fromlist=["analyze_plan", "expected_artifact_path"],
        )
        plan = {
            "goal": "synthetic",
            "rows": [
                {
                    "section": "active",
                    "app": "demo_app",
                    "path_name": "demo_path",
                    "baseline_artifact_stub": "docs/reports/goal835_baseline_demo_app_demo_path_<backend>_2026-04-23.json",
                    "required_baselines": ["cpu_oracle"],
                    "required_phases": ["build", "query"],
                    "minimum_repeated_runs": 3,
                    "comparable_metric_scope": "same synthetic compact summary",
                    "scale": {"copies": 7, "iterations": 3},
                    "claim_limit": "synthetic only",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_root = Path(tmpdir)
            row = plan["rows"][0]
            path = module.expected_artifact_path(row, "cpu_oracle", artifact_root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    {
                        "app": "demo_app",
                        "path_name": "demo_path",
                        "baseline_name": "cpu_oracle",
                        "status": "ok",
                        "correctness_parity": False,
                        "phase_separated": True,
                        "authorizes_public_speedup_claim": False,
                        "repeated_runs": 1,
                        "required_phase_coverage": ["build"],
                        "comparable_metric_scope": "same synthetic compact summary",
                        "benchmark_scale": {"copies": 1, "iterations": 3},
                    }
                ),
                encoding="utf-8",
            )
            payload = module.analyze_plan(plan, artifact_root)
            self.assertEqual(payload["status"], "needs_baselines")
            self.assertEqual(payload["invalid_artifact_count"], 1)
            errors = payload["rows"][0]["artifact_checks"][0]["errors"]
            self.assertIn("correctness_parity must be true", errors)
            self.assertTrue(any("repeated_runs" in error for error in errors))
            self.assertTrue(any("missing required phase coverage" in error for error in errors))
            self.assertIn("benchmark_scale does not match Goal835 plan", errors)

    def test_cli_writes_artifacts_and_exits_nonzero_when_baselines_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "readiness.json"
            output_md = Path(tmpdir) / "readiness.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/goal836_rtx_baseline_readiness_gate.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(completed.returncode, 1)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "needs_baselines")
            self.assertTrue(output_md.exists())


if __name__ == "__main__":
    unittest.main()
