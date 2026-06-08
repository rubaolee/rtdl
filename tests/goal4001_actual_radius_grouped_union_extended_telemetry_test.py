from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4001_actual_radius_exttelemetry_pod"
REPORT = ROOT / "docs" / "reports" / "goal4001_actual_radius_grouped_union_extended_telemetry_2026-06-08.md"


class Goal4001ActualRadiusGroupedUnionExtendedTelemetryTest(unittest.TestCase):
    def _artifact(self, profile: str) -> dict[str, object]:
        return json.loads((ARTIFACT_DIR / f"{profile}_65536.json").read_text(encoding="utf-8"))

    def _variants(self, profile: str) -> dict[str, dict[str, object]]:
        artifact = self._artifact(profile)
        self.assertEqual(artifact["goal"], "Goal4001")
        self.assertEqual(artifact["status"], "pass")
        boundary = artifact["claim_boundary"]
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertFalse(boundary["release_authorized"])
        row = artifact["rows"][0]
        return {variant["label"]: variant for variant in row["variants"]}

    def test_artifacts_use_actual_benchmark_radii(self) -> None:
        expected = {
            "clustered3d": 0.055,
            "road3d": 0.030,
            "ngsim_dense": 0.012,
        }
        for profile, radius in expected.items():
            artifact = self._artifact(profile)
            self.assertEqual(artifact["point_counts"], [65536])
            self.assertEqual(artifact["profile"], profile)
            self.assertAlmostEqual(float(artifact["radius"]), radius)
            self.assertEqual(artifact["repeats"], 3)

    def test_same_root_culling_is_required_at_actual_radii(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            variants = self._variants(profile)
            default = variants["same_root_on_direct_off"]
            no_cull = variants["same_root_off_direct_off"]
            self.assertGreater(
                float(no_cull["median_native_elapsed_sec"]),
                float(default["median_native_elapsed_sec"]),
            )
            telemetry = default["last_telemetry"]
            radius_candidates = int(telemetry[4])
            same_root_culled = int(telemetry[5])
            reported = int(telemetry[7])
            self.assertGreater(radius_candidates, 1_000_000)
            self.assertGreater(same_root_culled, radius_candidates * 0.99)
            self.assertLess(reported, radius_candidates * 0.01)

    def test_direct_side_effect_is_small_candidate_not_complete_solution(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            variants = self._variants(profile)
            default = variants["same_root_on_direct_off"]
            direct = variants["same_root_on_direct_on"]
            ratio = float(direct["median_native_elapsed_sec"]) / float(default["median_native_elapsed_sec"])
            self.assertLess(ratio, 1.02)
            self.assertEqual(int(direct["last_telemetry"][7]), 0)

    def test_report_records_diagnostic_boundary_and_next_direction(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`accept-with-boundary`",
            "actual RT-DBSCAN benchmark radii",
            "same-root culling is mandatory",
            "Direct side effects are a useful but small mode knob",
            "device-resident partition/convergence hybrid",
            "does not authorize release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
