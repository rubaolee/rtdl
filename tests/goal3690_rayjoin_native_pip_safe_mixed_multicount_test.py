from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal3690_rayjoin_native_pip_safe_mixed_multicount_2026-06-07.md"
ARTIFACT = ROOT / "docs/reports/goal3690_rayjoin_native_pip_safe_mixed_multicount_a5000/summary.json"


class Goal3690RayJoinNativePipSafeMixedMulticountTest(unittest.TestCase):
    def test_report_records_multicount_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("No implementation changed for Goal3690", report)
        self.assertIn("source commit: `9cfbc20d`", report)
        self.assertIn("geomean candidate speedup versus dense all-CuPy: `95.812x`", report)
        self.assertIn("not public RayJoin paper-reproduction evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_exact_multicount_packet(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3688.rayjoin_native_pip_safe_mixed_composite.v1")
        self.assertEqual(payload["source_commit_short"], "9cfbc20d")
        self.assertFalse(payload["goal3688_scoped_source_dirty"])
        self.assertEqual(payload["counts"], [512, 1024, 2048, 4096])
        self.assertTrue(payload["summary"]["all_counts_match"])
        self.assertEqual(payload["summary"]["row_count"], 4)
        self.assertGreater(payload["summary"]["geomean_native_pip_safe_mixed_speedup_vs_all_cupy"], 90.0)
        self.assertGreater(payload["summary"]["min_native_pip_safe_mixed_speedup_vs_all_cupy"], 50.0)
        self.assertFalse(payload["claim_boundary"]["release_authorized"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rayjoin_paper_reproduction_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        for row in payload["rows"]:
            self.assertTrue(row["all_counts_match"])
            self.assertGreater(row["native_pip_safe_mixed_speedup_vs_all_cupy"], 1.0)
            workloads = {item["workload"]: item for item in row["workloads"]}
            self.assertEqual(set(workloads), {"pip", "lsi", "overlay_seed"})
            for workload in workloads.values():
                self.assertTrue(workload["counts_match"])
                self.assertEqual(
                    workload["all_cupy_baseline"]["row_count"],
                    workload["candidate_route"]["row_count"],
                )
                self.assertGreater(workload["candidate_speedup_vs_cupy"], 1.0)


if __name__ == "__main__":
    unittest.main()
