from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2808_v2_5_current_head_canonical_harness_rerun_2026-05-31.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2808_current_head_canonical_harness_pod"
EXPECTED_COMMIT = "eba4de3cd0fc513e01410b4dd2bece7f55c1ac57"
EXPECTED_ARTIFACTS = (
    "goal2797_triangle_counting.json",
    "goal2798_librts.json",
    "goal2799_spatial_rayjoin.json",
    "goal2800_rtnn.json",
    "goal2801_hausdorff_xhd.json",
    "goal2802_rt_dbscan.json",
    "goal2803_barnes_hut.json",
)


class Goal2808V25CurrentHeadCanonicalHarnessRerunTest(unittest.TestCase):
    def _artifact(self, name: str) -> dict[str, object]:
        return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))

    def test_all_current_head_artifacts_pass_from_clean_a5000_commit(self) -> None:
        for name in EXPECTED_ARTIFACTS:
            with self.subTest(name=name):
                artifact = self._artifact(name)
                self.assertEqual(artifact["status"], "pass")
                self.assertEqual(artifact["source_commit"], EXPECTED_COMMIT)
                self.assertEqual(artifact["source_dirty"], [])
                self.assertIn("NVIDIA RTX A5000", str(artifact["gpu"]))

    def test_hardened_first_three_harnesses_emit_provenance(self) -> None:
        for name in EXPECTED_ARTIFACTS[:3]:
            with self.subTest(name=name):
                artifact = self._artifact(name)
                self.assertIn("source_commit", artifact)
                self.assertIn("source_dirty", artifact)
                self.assertIn("gpu", artifact)
                self.assertGreater(float(artifact["elapsed_sec"]), 0.0)

    def test_claim_boundaries_remain_false(self) -> None:
        for name in EXPECTED_ARTIFACTS:
            artifact = self._artifact(name)
            claim_boundary = artifact["claim_boundary"]
            for key, value in claim_boundary.items():
                if "claim_authorized" in key or "speedup_claim_authorized" in key or "reproduction_claim_authorized" in key:
                    with self.subTest(name=name, key=key):
                        self.assertFalse(value)
            self.assertFalse(claim_boundary["native_engine_customization"])

    def test_report_records_strong_and_weak_signals_without_release_authorization(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", text)
        self.assertIn("Goal2802", text)
        self.assertIn("3.936x to 4.887x", text)
        self.assertIn("Goal2803", text)
        self.assertIn("160.970x", text)
        self.assertIn("Hausdorff remains correct and RT-core-backed", text)
        self.assertIn("RTNN remains correct", text)
        self.assertIn("does not authorize a release", text)


if __name__ == "__main__":
    unittest.main()
