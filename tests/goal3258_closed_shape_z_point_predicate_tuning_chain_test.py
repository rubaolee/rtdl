from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3258_closed_shape_z_point_predicate_tuning_chain_2026-06-03.md"
G3256_DIRECT = ROOT / "docs" / "reports" / "goal3256_closed_shape_z_point_probe_pod_2026-06-03.json"
G3256_RAYJOIN = ROOT / "docs" / "reports" / "goal3256_rayjoin_z_point_same_slice_pod_2026-06-03.json"
G3257_DIRECT = ROOT / "docs" / "reports" / "goal3257_closed_shape_z_point_single_pass_probe_pod_2026-06-03.json"
G3257_RAYJOIN = ROOT / "docs" / "reports" / "goal3257_rayjoin_z_point_single_pass_same_slice_pod_2026-06-03.json"
G3258_DIRECT = ROOT / "docs" / "reports" / "goal3258_closed_shape_z_point_squared_boundary_probe_pod_2026-06-03.json"
G3258_RAYJOIN = ROOT / "docs" / "reports" / "goal3258_rayjoin_z_point_squared_boundary_same_slice_pod_2026-06-03.json"


class Goal3258ClosedShapeZPointPredicateTuningChainTest(unittest.TestCase):
    def _load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def test_report_records_full_tuning_chain_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Closed-Shape Z-Point Predicate Tuning Chain",
            "Goal3256 z-point probe",
            "Goal3257 single-pass predicate",
            "Goal3258 squared boundary predicate",
            "0.351587 ms",
            "1.69x",
            "does not authorize release",
            "not yet `RTDL beats RayJoin`",
        ):
            self.assertIn(phrase, text)

    def test_artifacts_are_clean_and_claim_bounded(self) -> None:
        for path in (G3256_DIRECT, G3256_RAYJOIN, G3257_DIRECT, G3257_RAYJOIN, G3258_DIRECT, G3258_RAYJOIN):
            data = self._load(path)
            if data.get("goal") == 3252:
                self.assertEqual(data["repo_state"]["source_dirty"], [])
                self.assertTrue(all(value is False for value in data["claim_boundary"].values()))
                self.assertTrue(data["comparison"]["all_counts_match"])
            else:
                self.assertEqual(data["source_dirty"], [])
                self.assertTrue(all(value is False for value in data["claim_boundary"].values()))
                rows = {row["workload"]: row for row in data["comparisons"]}
                self.assertEqual(rows["pip"]["rtdl_count"], 1430)
                self.assertEqual(rows["pip"]["count_contract_status"], "rayjoin_pip_count_not_visible")

    def test_direct_count_improves_monotonically_after_goal3256(self) -> None:
        g3256 = self._load(G3256_DIRECT)
        g3257 = self._load(G3257_DIRECT)
        g3258 = self._load(G3258_DIRECT)

        self.assertEqual(g3256["device_filtered_count"]["counts"], [1430] * 15)
        self.assertEqual(g3257["device_filtered_count"]["counts"], [1430] * 15)
        self.assertEqual(g3258["device_filtered_count"]["counts"], [1430] * 15)

        g3256_ms = g3256["device_filtered_count"]["median_sec"] * 1000.0
        g3257_ms = g3257["device_filtered_count"]["median_sec"] * 1000.0
        g3258_ms = g3258["device_filtered_count"]["median_sec"] * 1000.0

        self.assertAlmostEqual(g3256_ms, 0.5567297339439392)
        self.assertAlmostEqual(g3257_ms, 0.39563514292240143)
        self.assertAlmostEqual(g3258_ms, 0.3143921494483948)
        self.assertGreater(g3256_ms, g3257_ms)
        self.assertGreater(g3257_ms, g3258_ms)

    def test_same_slice_rayjoin_gap_moves_from_four_x_to_under_two_x(self) -> None:
        g3256 = self._load(G3256_RAYJOIN)
        g3257 = self._load(G3257_RAYJOIN)
        g3258 = self._load(G3258_RAYJOIN)

        def pip_row(data: dict) -> dict:
            return {row["workload"]: row for row in data["comparisons"]}["pip"]

        r3256 = pip_row(g3256)
        r3257 = pip_row(g3257)
        r3258 = pip_row(g3258)

        self.assertAlmostEqual(r3256["rtdl_prepared_query_ms_median"], 0.5485787987709045)
        self.assertAlmostEqual(r3257["rtdl_prepared_query_ms_median"], 0.39699114859104156)
        self.assertAlmostEqual(r3258["rtdl_prepared_query_ms_median"], 0.35158731043338776)
        self.assertGreater(r3256["rtdl_over_rayjoin_query_ratio"], 2.5)
        self.assertGreater(r3257["rtdl_over_rayjoin_query_ratio"], 1.8)
        self.assertLess(r3258["rtdl_over_rayjoin_query_ratio"], 1.7)

        phases = g3258["rtdl"]["pip"]["native_phase_samples"]
        self.assertTrue(all(sample["candidate_write_pass"] == 0.0 for sample in phases))
        self.assertTrue(all(sample["candidate_download"] == 0.0 for sample in phases))
        self.assertTrue(all(sample["exact_refine"] == 0.0 for sample in phases))


if __name__ == "__main__":
    unittest.main()
