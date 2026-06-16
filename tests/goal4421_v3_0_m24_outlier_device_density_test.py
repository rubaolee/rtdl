from __future__ import annotations

import json
from pathlib import Path
from unittest import mock
import unittest

from examples import rtdl_outlier_detection_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/apps/ml/rtdl_outlier_detection_app.py"
ADAPTERS = ROOT / "src/rtdsl/partner_adapters.py"
RUNNER = ROOT / "scripts/v3_0_m24_outlier_device_density_measure.py"
REPORT = ROOT / "docs/reports/goal4421_v3_0_m24_outlier_device_density_2026-06-15.md"
EVIDENCE_JSON = ROOT / "docs/reports/goal4421_v3_0_m24_outlier_device_density_65536_2026-06-15.json"
LARGE_EVIDENCE_JSON = ROOT / "docs/reports/goal4421_v3_0_m24_outlier_device_density_524288_2026-06-15.json"


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


def _fake_density_result() -> dict[str, object]:
    point_ids = (1, 2, 3, 4, 5, 6, 7, 8, 101, 102, 103, 104, 105, 106, 107, 108)
    neighbor_counts = (3, 3, 3, 3, 3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 1, 1)
    threshold_flags = (1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0)
    return {
        "columns": {
            "query_ids": _FakeNumbaColumn(point_ids),
            "neighbor_counts": _FakeNumbaColumn(neighbor_counts),
            "threshold_flags": _FakeNumbaColumn(threshold_flags),
        },
        "metadata": {
            "partner": "numba",
            "native_engine_row_contract": "generic_fixed_radius_count_threshold_2d_device_columns",
            "native_metadata": {
                "native_symbol": "rtdl_optix_write_prepared_fixed_radius_count_threshold_2d_device_query_columns",
                "native_acceleration_structure_required": True,
            },
        },
    }


class Goal4421V30M24OutlierDeviceDensityTest(unittest.TestCase):
    def test_partner_adapters_expose_numba_2d_prepared_output_columns(self) -> None:
        source = ADAPTERS.read_text(encoding="utf-8")
        self.assertIn("prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene", source)
        self.assertIn("fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns", source)
        self.assertIn('if partner == "numba":\n        cuda, np = _numba_cuda_stack_for_radius_graph()', source)
        self.assertNotIn("rtdl_optix_outlier", source.lower())

    def test_mocked_numba_route_matches_tiled_oracle_and_repeats_hot_window(self) -> None:
        fake_prepared = _FakePrepared()
        fake_columns = {"ids": object(), "x": object(), "y": object()}
        with mock.patch.object(app.rt, "point_rows_to_partner_columns", return_value=fake_columns) as to_columns:
            with mock.patch.object(
                app.rt,
                "prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene",
                return_value=fake_prepared,
            ) as prepare:
                with mock.patch.object(
                    app.rt,
                    "allocate_fixed_radius_count_threshold_2d_partner_device_output_columns",
                    return_value={"query_ids": object(), "neighbor_counts": object(), "threshold_flags": object()},
                ) as allocate:
                    with mock.patch.object(
                        app.rt,
                        "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns",
                        return_value=_fake_density_result(),
                    ) as run:
                        payload = app.run_app(
                            "optix_device_density",
                            copies=2,
                            output_mode="density_summary",
                            partner="numba",
                            query_repeat=2,
                            warmup=1,
                        )

        self.assertTrue(fake_prepared.closed)
        to_columns.assert_called_once()
        self.assertEqual(to_columns.call_args.kwargs["id_dtype"], "uint32")
        self.assertEqual(prepare.call_args.kwargs["partner"], "numba")
        self.assertEqual(allocate.call_args.kwargs["partner"], "numba")
        self.assertEqual(run.call_count, 3)
        self.assertEqual(payload["backend"], "optix_device_density")
        self.assertEqual(payload["partner"], "numba")
        self.assertEqual(payload["outlier_count"], 4)
        self.assertEqual(payload["outlier_point_ids"], [7, 8, 107, 108])
        self.assertTrue(payload["matches_oracle"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_device_density_threshold_columns")
        metadata = payload["partner_metadata"]
        self.assertEqual(metadata["front_door"], "fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns")
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["repeat"], 2)
        self.assertEqual(metadata["prepared_query_repeat_protocol"]["warmup"], 1)
        self.assertTrue(metadata["device_result_materialization_after_hot_window"])
        self.assertFalse(metadata["app_specific_native_engine_logic_allowed"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])

    def test_runner_records_both_partner_choices_and_compacts_payloads(self) -> None:
        source = RUNNER.read_text(encoding="utf-8")
        self.assertIn('for partner in ("cupy", "numba")', source)
        self.assertIn('"optix_device_density"', source)
        self.assertIn("_compact_app_row", source)
        self.assertIn("density_row_count", source)
        self.assertIn("--numba-cuda-home", source)

    def test_report_and_optional_evidence_capture_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Outlier device-density bridge", report)
        self.assertIn("generic prepared OptiX fixed-radius count-threshold", report)
        self.assertIn("CuPy and Numba", report)
        self.assertIn("not an outlier-specific native engine ABI", report)
        if not EVIDENCE_JSON.exists() or not LARGE_EVIDENCE_JSON.exists():
            self.skipTest("M24 pod evidence JSON has not been generated on this checkout")
        for path, point_count, outlier_count in (
            (EVIDENCE_JSON, 65_536, 16_384),
            (LARGE_EVIDENCE_JSON, 524_288, 131_072),
        ):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["parameters"]["point_count"], point_count)
                self.assertTrue(payload["comparison"]["all_match_oracle"])
                self.assertTrue(payload["comparison"]["outlier_counts_match"])
                self.assertTrue(payload["comparison"]["rt_core_accelerated"])
                rows = {row["partner"]: row for row in payload["rows"]}
                self.assertEqual({"cupy", "numba"}, set(rows))
                for row in rows.values():
                    self.assertEqual(row["outlier_count"], outlier_count)
                    self.assertTrue(row["device_result_materialization_after_hot_window"])
                    self.assertFalse(row["public_speedup_claim_authorized"])
                    self.assertFalse(row["app_specific_native_engine_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
