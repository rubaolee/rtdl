from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_benchmark_evidence_index.py"
DOC = ROOT / "docs" / "learn" / "benchmark_evidence_index.md"


class Goal4279BenchmarkEvidenceIndexTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=False,
        )

    def test_json_index_covers_all_ten_current_benchmark_apps(self) -> None:
        result = self._run("--json")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("current_v2_10_evidence_index_not_release_authorization", payload["status"])
        self.assertEqual("accept", payload["validation"]["status"])
        self.assertEqual(10, payload["summary"]["app_count"])
        self.assertEqual(10, len(payload["rows"]))

        apps = {row["app"] for row in payload["rows"]}
        self.assertEqual(
            {
                "hausdorff_xhd",
                "spatial_rayjoin",
                "rt_dbscan",
                "robot_collision",
                "contact_manifold",
                "raydb_style",
                "barnes_hut",
                "librts_spatial_index",
                "rtnn",
                "triangle_counting",
            },
            apps,
        )

    def test_index_commands_and_evidence_are_current_and_existing(self) -> None:
        payload = json.loads(self._run("--json").stdout)
        issues: list[str] = []

        for row in payload["rows"]:
            command_text = row["command_text"]
            if "examples/current/research_benchmarks/" not in command_text:
                issues.append(f"{row['app']}: command not current benchmark path")
            if "examples/v2_0" in command_text:
                issues.append(f"{row['app']}: stale examples/v2_0 command")
            for report in row["evidence_reports"]:
                if not report["exists"]:
                    issues.append(f"{row['app']}: missing {report['ref']} -> {report['path']}")

        for path in payload["cross_cutting_reports"]:
            if not (ROOT / path).is_file():
                issues.append(f"missing cross-cutting report: {path}")

        self.assertEqual([], issues)

    def test_index_is_non_authorizing(self) -> None:
        payload = json.loads(self._run("--json").stdout)
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["automatic_partner_selection_authorized"])

        for row in payload["rows"]:
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["broad_rt_core_claim_authorized"])
            self.assertFalse(row["paper_reproduction_claim_authorized"])

    def test_markdown_output_and_docs_are_linked_from_current_guides(self) -> None:
        result = self._run()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Current Benchmark Evidence Index", result.stdout)
        self.assertIn("spatial_rayjoin_pip_count_current_prepared_optix", result.stdout)
        self.assertIn("not a release or speedup authorization", result.stdout)

        docs = "\n".join(
            [
                DOC.read_text(encoding="utf-8"),
                (ROOT / "docs" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "learn" / "README.md").read_text(encoding="utf-8"),
                (ROOT / "examples" / "current" / "research_benchmarks" / "README.md").read_text(
                    encoding="utf-8"
                ),
            ]
        )
        self.assertIn("scripts/rtdl_benchmark_evidence_index.py", docs)
        self.assertIn("Benchmark Evidence Index", docs)
        self.assertIn("goal4215_current_benchmark_scale_profile_after_rtdbscan_policy", docs)
        self.assertNotIn("examples/v2_0", docs)
        self.assertNotIn("v2.6", docs)


if __name__ == "__main__":
    unittest.main()
