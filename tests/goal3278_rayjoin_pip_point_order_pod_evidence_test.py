from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3278_rayjoin_pip_point_order_locality_probe_2026-06-03.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3278_point_order_pod"


class Goal3278RayJoinPipPointOrderPodEvidenceTest(unittest.TestCase):
    def _artifact(self, name: str) -> dict:
        path = ARTIFACT_DIR / f"{name}.json"
        self.assertTrue(path.exists(), str(path))
        return json.loads(path.read_text(encoding="utf-8"))

    def test_report_records_bounded_morton_locality_win(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Morton-ordered probe packing",
            "source-clean rerun",
            "1.392x",
            "larger native locality/grouping primitive",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)

    def test_artifacts_are_source_clean_count_preserving_and_claim_blocked(self) -> None:
        for name in ("natural", "x_then_y", "y_then_x", "morton_xy"):
            data = self._artifact(name)
            pip = data["rtdl"]["pip"]

            self.assertEqual(data["source_dirty"], [])
            self.assertEqual(pip["counts"]["last"], 1430)
            self.assertTrue(pip["counts"]["consistent"])
            self.assertEqual(pip["count_mode"], "device_filtered_validated")
            self.assertEqual(pip["query_axis"], "z_point")
            self.assertEqual(pip["point_order_mode"], name)
            self.assertFalse(data["claim_boundary"]["release_authorized"])
            self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
            self.assertFalse(data["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
            self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_morton_is_best_measured_order_and_x_y_regresses(self) -> None:
        natural = self._artifact("natural")["rtdl"]["pip"]["prepared_query_ms"]["median"]
        x_then_y = self._artifact("x_then_y")["rtdl"]["pip"]["prepared_query_ms"]["median"]
        y_then_x = self._artifact("y_then_x")["rtdl"]["pip"]["prepared_query_ms"]["median"]
        morton = self._artifact("morton_xy")["rtdl"]["pip"]["prepared_query_ms"]["median"]

        self.assertLess(morton, natural)
        self.assertLess(morton, x_then_y)
        self.assertLess(morton, y_then_x)
        self.assertGreater(x_then_y, natural)

    def test_morton_improves_native_count_pass(self) -> None:
        natural = self._artifact("natural")["rtdl"]["pip"]["native_phase_samples"]
        morton = self._artifact("morton_xy")["rtdl"]["pip"]["native_phase_samples"]
        natural_count_pass = sorted(sample["candidate_count_pass"] for sample in natural)[len(natural) // 2]
        morton_count_pass = sorted(sample["candidate_count_pass"] for sample in morton)[len(morton) // 2]

        self.assertLess(morton_count_pass, natural_count_pass)


if __name__ == "__main__":
    unittest.main()
