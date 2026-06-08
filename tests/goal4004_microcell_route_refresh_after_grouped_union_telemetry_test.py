from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal4004_microcell_route_refresh_pod"
REPORT = ROOT / "docs" / "reports" / "goal4004_microcell_route_refresh_after_grouped_union_telemetry_2026-06-08.md"


class Goal4004MicrocellRouteRefreshAfterGroupedUnionTelemetryTest(unittest.TestCase):
    def _payload(self, profile: str, route: str) -> dict[str, object]:
        return json.loads((ARTIFACT_DIR / f"{profile}_{route}.json").read_text(encoding="utf-8"))

    def test_microcell_route_matches_signatures_but_is_slower(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            grouped = self._payload(profile, "grouped")
            microcell = self._payload(profile, "microcell")
            self.assertEqual(grouped["signature"], microcell["signature"])
            ratio = float(microcell["elapsed_sec"]) / float(grouped["elapsed_sec"])
            self.assertGreater(ratio, 20.0)
            self.assertTrue(microcell["metadata"]["cell_graph_fast_path_active"])
            self.assertEqual(microcell["metadata"]["cell_graph_granularity"], "clique_safe_microcell")

    def test_grouped_stream_remains_current_baseline(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            grouped = self._payload(profile, "grouped")
            self.assertEqual(
                grouped["metadata"]["native_engine_row_contract"],
                "generic_prepared_fixed_radius_grouped_union_3d_all_items_self_device_parent_workspace",
            )
            self.assertTrue(grouped["metadata"]["grouped_union_same_root_culling_enabled"])
            self.assertFalse(grouped["metadata"]["grouped_union_direct_side_effect_enabled"])

    def test_claim_boundaries_remain_closed(self) -> None:
        for profile in ("clustered3d", "road3d", "ngsim_dense"):
            for route in ("grouped", "microcell"):
                payload = self._payload(profile, route)
                boundary = payload["claim_boundary"]
                self.assertFalse(boundary["paper_dataset_reproduction"])
                self.assertFalse(boundary["paper_speedup_claim_authorized"])
                self.assertFalse(boundary["native_dbscan_abi_added"])

    def test_report_rejects_microcell_as_performance_route(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        for fragment in [
            "`reject-as-performance-route`",
            "much slower than the current RTDL/OptiX grouped-stream route",
            "clique_safe_microcell",
            "do not reuse the old partner microcell path as the promoted route",
            "native/device-resident partition assist",
            "does not authorize",
            "release",
        ]:
            self.assertIn(fragment, report)


if __name__ == "__main__":
    unittest.main()
