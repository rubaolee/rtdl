from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4079_current_grouped_union_root_work_refresh_2026-06-09.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4079_current_grouped_union_root_work_refresh_pod"


class Goal4079CurrentGroupedUnionRootWorkRefreshTest(unittest.TestCase):
    def _load_default(self, name: str) -> tuple[dict, dict, list[int]]:
        payload = json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
        row = payload["rows"][0]
        default = next(
            variant for variant in row["variants"]
            if variant["label"] == "same_root_on_direct_off"
        )
        telemetry = [int(value) for value in default["last_telemetry"]]
        return payload, default, telemetry

    def test_artifacts_are_current_head_ten_counter_diagnostics(self) -> None:
        for name in ["clustered3d_65536.json", "road3d_65536.json", "ngsim_dense_65536.json"]:
            payload, default, telemetry = self._load_default(name)
            self.assertEqual(payload["goal"], "Goal4079")
            self.assertEqual(payload["source_commit"][:8], "f80245b7")
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["telemetry_counter_capacity"], 10)
            self.assertEqual(default["last_metadata"]["grouped_union_telemetry_counter_count"], 10)
            self.assertTrue(default["last_metadata"]["grouped_union_root_read_telemetry_enabled"])
            self.assertEqual(len(telemetry), 10)
            self.assertFalse(payload["claim_boundary"]["performance_claim_authorized"])
            self.assertFalse(payload["claim_boundary"]["release_authorized"])

    def test_default_route_candidate_and_root_work_is_large(self) -> None:
        expected_minimums = {
            "clustered3d_65536.json": (250_000_000, 500_000_000),
            "road3d_65536.json": (80_000_000, 160_000_000),
            "ngsim_dense_65536.json": (10_000_000, 20_000_000),
        }
        for name, (min_candidates, min_root_calls) in expected_minimums.items():
            _, _, telemetry = self._load_default(name)
            self.assertGreater(telemetry[4], min_candidates)
            self.assertGreater(telemetry[8], min_root_calls)
            self.assertGreater(telemetry[5], telemetry[7])
            self.assertGreater(telemetry[9], telemetry[8])

    def test_report_preserves_boundary_and_next_primitive_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "not production-route timings",
            "partition-convergence hybrid",
            "fixed-radius grouped-union work",
            "not as DBSCAN",
            "does not authorize release",
            "reduce candidate enumeration and root-read work together",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
