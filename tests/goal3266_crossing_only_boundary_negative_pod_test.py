from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3266_crossing_only_boundary_negative_probe_2026-06-03.md"
NEGATIVE = ROOT / "docs" / "reports" / "goal3266_crossing_only_boundary_negative_probe_pod_2026-06-03.json"
CONTROL = ROOT / "docs" / "reports" / "goal3266_inclusive_boundary_control_z_point_same_slice_pod_2026-06-03.json"


class Goal3266CrossingOnlyBoundaryNegativePodTest(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _row(self, artifact: dict, workload: str) -> dict:
        return {row["workload"]: row for row in artifact["comparisons"]}[workload]

    def test_negative_artifact_records_validation_failure(self) -> None:
        data = self._load(NEGATIVE)

        self.assertEqual(data["schema"], "rtdl.goal3266.crossing_only_boundary_negative_probe.v1")
        self.assertTrue(data["rtdl_commit"].startswith("65eee5c5"))
        self.assertEqual(data["source_dirty"], [])
        self.assertFalse(data["crossing_only_validation_passed"])
        self.assertEqual(data["device_filtered_boundary_mode"], "crossing_only")
        self.assertEqual(data["crossing_only_count"], 129)
        self.assertEqual(data["exact_inclusive_count"], 1430)
        self.assertIn("129 != 1430", data["error"])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_inclusive_control_is_clean_count_preserving_and_non_claiming(self) -> None:
        data = self._load(CONTROL)
        pip = self._row(data, "pip")
        lsi = self._row(data, "lsi")

        self.assertTrue(data["rtdl_commit"].startswith("65eee5c5"))
        self.assertEqual(data["source_dirty"], [])
        self.assertEqual(data["rtdl"]["pip"]["query_axis"], "z_point")
        self.assertEqual(data["rtdl"]["pip"]["device_filtered_boundary_mode"], "inclusive")
        self.assertEqual(pip["rtdl_count"], 1430)
        self.assertEqual(lsi["rtdl_count"], 269)
        self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
        self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_report_draws_negative_conclusion_and_next_target(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Crossing-Only Boundary Negative Probe",
            "129 != 1430",
            "not a legal optimization",
            "boundary-heavy",
            "slightly slower than Goal3264",
            "shape-local edge blocking",
            "warp-cooperative edge evaluation",
            "does not authorize release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
