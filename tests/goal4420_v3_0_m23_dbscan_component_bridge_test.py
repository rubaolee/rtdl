from __future__ import annotations

import json
from pathlib import Path
from unittest import mock
import unittest

from examples import rtdl_dbscan_clustering_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/apps/ml/rtdl_dbscan_clustering_app.py"
RUNNER = ROOT / "scripts/v3_0_m23_dbscan_component_bridge_measure.py"
REPORT = ROOT / "docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_65536_2026-06-15.json"
LARGE_EVIDENCE_JSON = ROOT / "docs/reports/goal4420_v3_0_m23_dbscan_component_bridge_524288_2026-06-15.json"


class _FakePrepared:
    def __init__(self) -> None:
        self.closed = False

    def __enter__(self) -> "_FakePrepared":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.closed = True


class _FakeHostColumn:
    def __init__(self, values) -> None:
        self._values = list(values)

    def tolist(self) -> list[int]:
        return list(self._values)


class _FakeNumbaColumn:
    def __init__(self, values) -> None:
        self._values = list(values)

    def copy_to_host(self) -> _FakeHostColumn:
        return _FakeHostColumn(self._values)


def _fake_component_result() -> dict[str, object]:
    point_ids = (1, 2, 3, 4, 5, 6, 7, 8, 101, 102, 103, 104, 105, 106, 107, 108)
    component_labels = (1, 1, 1, 1, 5, 5, 5, -1, 101, 101, 101, 101, 105, 105, 105, -1)
    is_core = (1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0)
    neighbor_counts = (3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 1)
    return {
        "columns": {
            "point_ids": _FakeNumbaColumn(point_ids),
            "component_labels": _FakeNumbaColumn(component_labels),
            "is_core": _FakeNumbaColumn(is_core),
            "neighbor_counts": _FakeNumbaColumn(neighbor_counts),
        },
        "metadata": {
            "partner_reference_contract": "generic_prepared_optix_numba_grouped_stream_component_labels_3d",
            "native_engine_row_contract": "generic_prepared_fixed_radius_grouped_union_3d_self_device_workspaces",
            "native_execution_path": "prepared_rt_core_grouped_union_3d_self_query",
            "rt_core_accelerated": True,
            "materializes_neighbor_rows": False,
            "materializes_directed_adjacency_stream": False,
        },
    }


class Goal4420V30M23DbscanComponentBridgeTest(unittest.TestCase):
    def test_app_exposes_grouped_stream_component_backend_without_native_dbscan_abi(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn('"optix_grouped_stream_components"', source)
        self.assertIn("prepare_v2_8_fixed_radius_graph_component_continuation_3d", source)
        self.assertIn("fixed_radius_graph_component_labels_3d_v2_8", source)
        self.assertIn("dbscan_app_optix_grouped_stream_component_labels", source)
        self.assertIn('"app_specific_native_engine_logic_allowed": False', source)
        self.assertIn('"automatic_partner_selection_authorized": False', source)
        self.assertNotIn("rtdl_optix_dbscan", source.lower())

    def test_mocked_numba_route_matches_tiled_oracle_and_repeats_hot_window(self) -> None:
        fake_prepared = _FakePrepared()
        with mock.patch.object(
            app.rt,
            "prepare_v2_8_fixed_radius_graph_component_continuation_3d",
            return_value=fake_prepared,
        ) as prepare:
            with mock.patch.object(
                app.rt,
                "fixed_radius_graph_component_labels_3d_v2_8",
                return_value=_fake_component_result(),
            ) as run:
                payload = app.run_app(
                    "optix_grouped_stream_components",
                    copies=2,
                    partner="numba",
                    query_repeat=2,
                    warmup=1,
                )

        self.assertTrue(fake_prepared.closed)
        self.assertEqual(run.call_count, 3)
        prepare_kwargs = prepare.call_args.kwargs
        self.assertEqual(prepare_kwargs["backend"], "optix")
        self.assertEqual(prepare_kwargs["partner"], "numba")
        self.assertEqual(prepare_kwargs["strategy"], "grouped_stream")
        prepared_points = prepare.call_args.args[0]
        self.assertEqual(len(prepared_points), 16)
        self.assertTrue(all(float(point.z) == 0.0 for point in prepared_points))

        self.assertEqual(payload["backend"], "optix_grouped_stream_components")
        self.assertEqual(payload["partner"], "numba")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["cluster_sizes"], {1: 4, 2: 3, 3: 4, 4: 3})
        self.assertEqual(payload["noise_point_ids"], [8, 108])
        self.assertEqual(payload["core_count"], 14)
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_grouped_stream_component_labels")
        metadata = payload["partner_metadata"]
        self.assertEqual(metadata["front_door"], "v2_8_fixed_radius_graph_component_continuation_3d")
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["repeat"], 2)
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["warmup"], 1)
        self.assertTrue(metadata["device_result_materialization_after_hot_window"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_runner_records_both_partner_choices_and_compacts_payloads(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn('for partner in ("cupy", "numba")', source)
        self.assertIn('"optix_grouped_stream_components"', source)
        self.assertIn("_compact_app_row", source)
        self.assertIn("cluster_row_count", source)
        self.assertIn("--numba-cuda-home", source)

    def test_report_and_optional_evidence_capture_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("DBSCAN component-label bridge", report)
        self.assertIn("generic fixed-radius graph component", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("not a DBSCAN-specific native engine ABI", report)
        if not EVIDENCE_JSON.exists() or not LARGE_EVIDENCE_JSON.exists():
            self.skipTest("M23 pod evidence JSON has not been generated on this checkout")
        for path, point_count, cluster_count in (
            (EVIDENCE_JSON, 65_536, 16_384),
            (LARGE_EVIDENCE_JSON, 524_288, 131_072),
        ):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["parameters"]["point_count"], point_count)
                self.assertTrue(payload["comparison"]["all_match_oracle"])
                self.assertTrue(payload["comparison"]["cluster_size_signatures_match"])
                self.assertTrue(payload["comparison"]["rt_core_accelerated"])
                rows = {row["partner"]: row for row in payload["rows"]}
                self.assertEqual({"cupy", "numba"}, set(rows))
                for row in rows.values():
                    self.assertEqual(row["cluster_size_signature"]["cluster_count"], cluster_count)
                    self.assertTrue(row["device_result_materialization_after_hot_window"])
                    self.assertFalse(row["public_speedup_claim_authorized"])
                    self.assertFalse(row["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
