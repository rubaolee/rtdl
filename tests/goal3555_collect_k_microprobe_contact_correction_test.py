from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "docs" / "reports" / "goal3555_collect_k_microprobe_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3555_collect_k_microprobe_contact_correction_2026-06-06.md"


class Goal3555CollectKMicroprobeContactCorrectionTest(unittest.TestCase):
    def test_collect_and_validate_are_not_stable_v28_regressions(self) -> None:
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
        v23 = payload["v23"]
        v28 = payload["v28"]

        self.assertEqual(v23["row_container_type"], "tuple")
        self.assertEqual(v28["row_container_type"], "tuple")
        self.assertEqual(v23["row0_type"], "tuple")
        self.assertEqual(v28["row0_type"], "tuple")
        self.assertEqual(v23["row_count"], 4096)
        self.assertEqual(v28["row_count"], 4096)

        collect_speedup = v23["collect_median_sec"] / v28["collect_median_sec"]
        validate_speedup = v23["validate_median_sec"] / v28["validate_median_sec"]
        combined_speedup = v23["combined_median_sec"] / v28["combined_median_sec"]

        self.assertGreater(collect_speedup, 1.1)
        self.assertGreater(validate_speedup, 1.1)
        self.assertGreater(combined_speedup, 1.1)

    def test_report_blocks_bogus_source_change_and_names_rtnn_next(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("not the stable contact-manifold regression", text)
        self.assertIn("avoid touching the app-agnostic collector", text)
        self.assertIn("RTNN", text)
        self.assertIn("diagnostic evidence only", text)


if __name__ == "__main__":
    unittest.main()
