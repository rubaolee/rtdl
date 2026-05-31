from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2758_reusable_hit_stream_buffer_perf_probe.py"
REPORT = ROOT / "docs/reports/goal2758_reusable_hit_stream_buffer_perf_probe_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal2758_pod_artifacts"


class Goal2758ReusableHitStreamBufferPerfProbeTest(unittest.TestCase):
    def test_probe_script_compares_only_generic_output_ownership_modes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("native_owned", source)
        self.assertIn("caller_owned_reusable", source)
        self.assertIn("ray_triangle_hit_stream_device_columns", source)
        self.assertIn("ray_triangle_hit_stream_into_device_columns", source)
        self.assertIn("prepare_ray_triangle_hit_stream_device_column_buffers", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_authorized": False', source)
        for forbidden in ("raydb", "database", "dbscan", "rayjoin", "hausdorff"):
            self.assertNotIn(forbidden, source.lower())

    def test_pod_artifacts_record_expected_sizes_and_claim_boundaries(self) -> None:
        artifacts = sorted(ARTIFACT_DIR.glob("goal2758_reusable_hit_stream_buffer_perf*.json"))
        self.assertGreaterEqual(len(artifacts), 2)
        observed_sizes: set[int] = set()
        for artifact in artifacts:
            payload = json.loads(artifact.read_text(encoding="utf-8"))
            self.assertEqual(payload["goal"], "goal2758")
            self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(payload["claim_boundary"]["true_zero_copy_authorized"])
            self.assertTrue(payload["claim_boundary"]["compares_output_allocation_strategy_only"])
            for size, result in payload["sizes"].items():
                observed_sizes.add(int(size))
                self.assertIn("native_owned", result)
                self.assertIn("caller_owned_reusable", result)
                self.assertIn("ratios", result)
                for mode in ("native_owned", "caller_owned_reusable"):
                    summary = result[mode]["summary"]
                    self.assertGreater(summary["sample_count"], 0)
                    self.assertEqual(summary["row_count_min"], int(size))
                    self.assertEqual(summary["row_count_max"], int(size))
        self.assertTrue({1024, 8192, 32768, 131072, 524288}.issubset(observed_sizes))

    def test_report_keeps_perf_claim_internal_and_bounded(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("not a whole-app benchmark", report)
        self.assertIn("This goal does not authorize", report)
        self.assertIn("public speedup claims", report)
        self.assertIn("true zero-copy claims", report)
        self.assertIn("0.734x", report)
        self.assertIn("Goal2754 gap", report)


if __name__ == "__main__":
    unittest.main()
