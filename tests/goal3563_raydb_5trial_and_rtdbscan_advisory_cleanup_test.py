from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "reports" / "goal3563_raydb_5trial_and_advisory_cleanup_a5000"
SUMMARY = ARTIFACT / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3563_raydb_5trial_and_rtdbscan_advisory_cleanup_2026-06-06.md"
REGISTRY = ROOT / "scripts" / "goal2626_benchmark_embree_optix_baseline.py"
OVERLAY = ROOT / "docs" / "patches" / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch"


class Goal3563RayDBAndRTDBSCANAdvisoryCleanupTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

    def test_raydb_five_trial_probe_records_count_deescalation_and_sum_watch(self) -> None:
        raydb = self.payload["raydb"]
        self.assertEqual(raydb["trials"], 5)
        self.assertEqual(raydb["repeat"], 20000)
        self.assertEqual(raydb["warmup"], 2)

        count = raydb["by_mode"]["count"]
        raydb_sum = raydb["by_mode"]["sum"]
        self.assertEqual(len(count["values"]["v23"]), 5)
        self.assertEqual(len(count["values"]["v28"]), 5)
        self.assertEqual(len(raydb_sum["values"]["v23"]), 5)
        self.assertEqual(len(raydb_sum["values"]["v28"]), 5)

        self.assertGreater(float(count["v28_speedup_vs_v23"]), 1.0)
        self.assertGreater(float(raydb_sum["v28_speedup_vs_v23"]), 0.94)
        self.assertLess(float(raydb_sum["v28_speedup_vs_v23"]), 0.98)

    def test_rt_dbscan_seed_repeat4_has_three_measured_samples(self) -> None:
        section = self.payload["rt_dbscan_seed_repeat4"]
        self.assertEqual(section["repeat"], 4)
        self.assertEqual(section["warmup"], 1)
        self.assertGreater(float(section["v28_speedup_vs_v23"]), 1.0)
        for row in section["runs"]:
            self.assertEqual(row["repeat"], 4)
            self.assertEqual(row["warmup"], 1)
            self.assertEqual(row["measured_run_count"], 3)

    def test_registry_and_overlay_document_repeat_semantics(self) -> None:
        registry = REGISTRY.read_text(encoding="utf-8")
        start = registry.index('case_id="rt_dbscan_optix_grouped_stream"')
        end = registry.index('case_id="robot_collision_embree_prepared_buffers"')
        case = registry[start:end]
        self.assertIn('"--warmup"', case)
        self.assertIn('"1"', case)
        self.assertIn('"--repeat"', case)
        self.assertIn('"4"', case)

        overlay = OVERLAY.read_text(encoding="utf-8")
        self.assertIn("Goal3547 overlay note, updated by Goal3563", overlay)
        self.assertIn("median-of-measured-repeats", overlay)
        self.assertIn("pre-overlay historical `elapsed_sec`", overlay)

    def test_report_and_artifact_keep_claim_boundaries_closed(self) -> None:
        boundary = self.payload["claim_boundary"]
        for key, value in boundary.items():
            if key == "internal_results_only":
                self.assertIs(value, True)
            else:
                self.assertIs(value, False, key)

        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("RayDB sum should no longer be described as pure one-run noise", text)
        self.assertIn("does not authorize", text)
        self.assertIn("public v2.9 speedup claims", text)


if __name__ == "__main__":
    unittest.main()
