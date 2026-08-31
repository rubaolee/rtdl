from __future__ import annotations

from pathlib import Path
import unittest

from rtdsl.v2_8_benchmark_runtime_gap import V2_8_PROMOTED_BENCHMARK_APPS
from rtdsl.v2_9_benchmark_adequacy import (
    V2_9_BENCHMARK_ADEQUACY_VERSION,
    summarize_v2_9_benchmark_adequacy,
    validate_v2_9_benchmark_adequacy,
    v2_9_benchmark_adequacy,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3786_current_benchmark_adequacy_after_hiprt_closeout_2026-06-07.md"


class Goal3786CurrentBenchmarkAdequacyAfterHiprtCloseoutTest(unittest.TestCase):
    def test_current_adequacy_version_and_counts(self) -> None:
        self.assertEqual(
            V2_9_BENCHMARK_ADEQUACY_VERSION,
            "rtdl.v2_10.benchmark_adequacy_after_goal3820.v2",
        )
        validation = validate_v2_9_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = summarize_v2_9_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertEqual(summary["row_count"], 10)
        self.assertEqual(summary["numba_reference_needed_apps"], ())
        self.assertEqual(summary["adequacy_counts"]["needs_major_followup"], 0)

    def test_all_rows_are_ready_for_amd_functional_pod_without_claims(self) -> None:
        rows = v2_9_benchmark_adequacy()
        self.assertEqual({row["app"] for row in rows}, set(V2_8_PROMOTED_BENCHMARK_APPS))
        for row in rows:
            self.assertIn("ready for AMD functional pod", row["amd_hiprt_readiness"])
            self.assertIn("Goal3784", row["amd_hiprt_readiness"])
            self.assertNotIn("needs HIPRT", row["amd_hiprt_readiness"])
            self.assertNotIn("compatibility-only", row["amd_hiprt_readiness"].lower())
            self.assertFalse(row["needs_numba_reference"], row["app"])
            self.assertFalse(row["release_authorized"], row["app"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["app"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["app"])

    def test_report_covers_current_state_without_old_hiprt_gap_language(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3786", text)
        self.assertIn(V2_9_BENCHMARK_ADEQUACY_VERSION, text)
        for app in V2_8_PROMOTED_BENCHMARK_APPS:
            self.assertIn(f"`{app}`", text)
        self.assertIn("ready for AMD functional pod", text)
        self.assertIn("Goal3785 runner", text)
        self.assertIn("Goal3822", text)
        self.assertIn("front-door hardening", text)
        self.assertIn("does not authorize", text)
        self.assertNotIn("needs HIPRT mapping", text)
        self.assertNotIn("HIPRT nearest-witness and grouped-max parity", text)


if __name__ == "__main__":
    unittest.main()
