from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2405_rt_dbscan_rt_count_threshold_device_columns_pod"
REPORT = ROOT / "docs" / "reports" / "goal2405_rt_dbscan_rt_count_threshold_device_columns_2026-05-19.md"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


def _mode_rows(payload: dict[str, object], mode: str) -> list[dict[str, object]]:
    rows = payload["rows"]
    assert isinstance(rows, list)
    return [row for row in rows if isinstance(row, dict) and row.get("mode") == mode]


def _median_tail_seconds(payload: dict[str, object], mode: str) -> float:
    rows = _mode_rows(payload, mode)
    values = [float(row["app_elapsed_sec"]) for row in rows]
    return statistics.median(values[1:])


class Goal2405RtDbscanRtCountThresholdDeviceColumnsPodEvidenceTest(unittest.TestCase):
    def test_environment_records_pod_and_build_context(self) -> None:
        environment = (ARTIFACT_DIR / "environment.txt").read_text(encoding="utf-8")

        self.assertIn("root@69.30.85.177 -p 22055", environment)
        self.assertIn("base_head=61bc82dd05dc83cf48aaabc3b302a80e64dc7159", environment)
        self.assertIn("NVIDIA RTX A5000, 570.211.01", environment)
        self.assertIn("v8.1.0", environment)
        self.assertIn("libnvrtc.so.12", environment)

    def test_repeat_artifacts_match_signatures_and_mark_rt_core_path(self) -> None:
        for name in (
            "clustered3d_repeat4.json",
            "road3d_repeat4.json",
            "clustered3d_131072_repeat3.json",
            "road3d_131072_repeat3.json",
        ):
            with self.subTest(name=name):
                payload = _load(name)
                self.assertTrue(payload["signatures_match"])
                rt_rows = _mode_rows(payload, "optix_rt_core_flags_cupy_grid_components_3d")
                self.assertGreaterEqual(len(rt_rows), 2)
                for row in rt_rows:
                    self.assertTrue(row["rt_core_accelerated"])
                    self.assertFalse(row["materializes_neighbor_rows"])
                    self.assertIsNotNone(row["optix_rt_count_threshold_sec"])
                    self.assertIsNotNone(row["cupy_component_continuation_sec"])

    def test_new_rt_path_improves_prior_optix_backend_bridge_at_4096(self) -> None:
        for name in ("clustered3d_repeat4.json", "road3d_repeat4.json"):
            with self.subTest(name=name):
                payload = _load(name)
                prior = _median_tail_seconds(payload, "optix_core_flags_cupy_grid_components_3d")
                current = _median_tail_seconds(payload, "optix_rt_core_flags_cupy_grid_components_3d")
                self.assertLess(current, prior)

    def test_dense_clustered_scale_probe_has_crossover_but_sparse_road_boundary_remains(self) -> None:
        clustered = _load("clustered3d_131072_repeat3.json")
        road = _load("road3d_131072_repeat3.json")

        clustered_cupy = _median_tail_seconds(clustered, "partner_cupy_grid_components_3d")
        clustered_rt = _median_tail_seconds(clustered, "optix_rt_core_flags_cupy_grid_components_3d")
        road_cupy = _median_tail_seconds(road, "partner_cupy_grid_components_3d")
        road_rt = _median_tail_seconds(road, "optix_rt_core_flags_cupy_grid_components_3d")

        self.assertLess(clustered_rt, clustered_cupy)
        self.assertGreater(road_rt, road_cupy)

    def test_report_states_accept_with_boundary_and_next_generic_runtime_gap(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("true OptiX RT traversal", report)
        self.assertIn("not RT-DBSCAN paper reproduction", report)
        self.assertIn("not true zero-copy", report)
        self.assertIn("device-resident radius-graph component continuation", report)
        self.assertIn("not be a DBSCAN-native ABI", report)


if __name__ == "__main__":
    unittest.main()
