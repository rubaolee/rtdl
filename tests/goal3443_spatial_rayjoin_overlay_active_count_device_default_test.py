from __future__ import annotations

from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
GOAL3438_SCRIPT = ROOT / "scripts" / "goal3438_spatial_rayjoin_prepared_subroute_reuse_probe.py"
GOAL3441_SCRIPT = ROOT / "scripts" / "goal3441_shape_pair_active_count_phase_timing_probe.py"
GOAL3442_SCRIPT = ROOT / "scripts" / "goal3442_shape_pair_active_count_device_continuation_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal3443_spatial_rayjoin_overlay_active_count_device_default_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3443_spatial_rayjoin_overlay_active_count_device_default_pod_2026-06-05.json"


class Goal3443SpatialRayJoinOverlayActiveCountDeviceDefaultTest(unittest.TestCase):
    def test_app_default_delegates_to_device_continuation_and_keeps_host_oracle(self) -> None:
        app = APP.read_text(encoding="utf-8")

        default_start = app.index("    def run_packed_left(\n", app.index("class PreparedRayJoinOptixShapePairActiveCount"))
        host_start = app.index("    def run_packed_left_host_exact(", default_start)
        default_body = app[default_start:host_start]

        self.assertIn("return self.run_packed_left_device_continuation(", default_body)
        self.assertIn("def run_packed_left_host_exact(", app)
        self.assertIn("def run_packed_left_device_continuation(", app)

    def test_probes_pin_their_intended_routes(self) -> None:
        goal3438 = GOAL3438_SCRIPT.read_text(encoding="utf-8")
        goal3441 = GOAL3441_SCRIPT.read_text(encoding="utf-8")
        goal3442 = GOAL3442_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("active_count_device_continuation_sec", goal3438)
        self.assertIn("run_packed_left_host_exact", goal3441)
        self.assertIn("run_packed_left_host_exact", goal3442)
        self.assertIn("run_packed_left_device_continuation", goal3442)

    def test_docs_record_default_and_boundaries(self) -> None:
        readme = README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "device-side active-count continuation by default",
            "only the scalar count is copied back",
            "run_packed_left_host_exact",
        ):
            self.assertIn(phrase, readme)
        for phrase in (
            "Goal3443",
            "app-layer default change",
            "generic native primitive",
            "does not authorize release",
        ):
            self.assertIn(phrase, report)

    @unittest.skipUnless(ARTIFACT.exists(), "Goal3443 pod artifact pending")
    def test_pod_artifact_records_device_default_overlay_route(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        overlay = payload["routes"]["overlay_active_count"]
        self.assertEqual(payload["schema"], "rtdl.goal3438.spatial_rayjoin_prepared_subroute_reuse.v1")
        self.assertTrue(all(value is False for value in payload["claim_boundary"].values()))
        self.assertEqual(overlay["row_counts"], [4543, 4543, 4543, 4543])
        self.assertEqual(overlay["route"], "prepared_optix_shape_pair_active_count_reuse")
        for run in overlay["runs"]:
            self.assertIn("active_count_device_continuation_sec", run["phases_sec"])
            self.assertEqual(
                run["native_phase_timings"]["mode"],
                "active_count_device_continuation",
            )


if __name__ == "__main__":
    unittest.main()
