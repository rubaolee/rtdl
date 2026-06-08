from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "rtdl_rtnn_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rtnn" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal3886_rtnn_prepared_session_reuse_idiom_2026-06-08.md"


def _run_app(*args: str) -> dict:
    completed = subprocess.run(
        [sys.executable, str(APP), *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class Goal3886RtnnPreparedSessionReuseIdiomTest(unittest.TestCase):
    def test_cli_exposes_prepared_session_reuse_idiom(self) -> None:
        help_text = subprocess.check_output(
            [sys.executable, str(APP), "--help"],
            cwd=ROOT,
            text=True,
        )
        self.assertIn("prepared_session_reuse_idiom", help_text)

    def test_reuse_idiom_records_live_miss_put_hit_without_native_runner(self) -> None:
        payload = _run_app(
            "--mode",
            "prepared_session_reuse_idiom",
            "--point-count",
            "16",
            "--radius",
            "0.02",
            "--k",
            "8",
            "--distribution",
            "uniform",
        )

        self.assertEqual(payload["mode"], "prepared_session_reuse_idiom")
        self.assertTrue(payload["live_helper_invoked"])
        self.assertFalse(payload["native_runner_invoked"])
        self.assertFalse(payload["performance_evidence"])
        self.assertEqual(payload["prepared_call_count"], 1)
        self.assertEqual(payload["cache_hit_sequence"], [False, True])
        self.assertEqual(
            [row["event"] for row in payload["cache_event_log"]],
            ["miss", "put", "hit"],
        )

        metadata = payload["prepared_session_residency"]
        self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
        self.assertTrue(metadata["explicit_cache_enabled_for_this_demo"])
        self.assertFalse(metadata["cache_enabled_by_default"])
        self.assertEqual(metadata["cache_key"]["primitive"], "fixed_radius_neighbors_3d_ranked_summary")
        self.assertTrue(metadata["policy"]["cache_enabled"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

        for key in (
            "native_engine_customization",
            "full_rtnn_paper_reproduction",
            "public_speedup_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "amd_performance_claim_authorized",
        ):
            self.assertFalse(payload["claim_boundary"][key], key)
        self.assertTrue(payload["claim_boundary"]["not_performance_evidence"])

    def test_readme_and_report_document_non_performance_boundary(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")
        for text in (readme, report):
            self.assertIn("prepared_session_reuse_idiom", text)
            self.assertIn("get_or_prepare_explicit_session", text)
            self.assertIn("miss", text)
            self.assertIn("put", text)
            self.assertIn("hit", text)
            self.assertIn("not", text.lower())
            self.assertIn("performance", text.lower())
        self.assertIn("native_runner_invoked = false", report)
        self.assertIn("performance_evidence = false", report)


if __name__ == "__main__":
    unittest.main()
