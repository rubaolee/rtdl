from __future__ import annotations

import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_fixed_radius as v4_fixed_radius


class FakePrepared:
    def __init__(self) -> None:
        self.closed = False
        self.entered = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.closed = True

    def close(self) -> None:
        self.closed = True


class V4FixedRadiusDeviceArrayApiTest(unittest.TestCase):
    def test_claim_boundary_allows_only_measured_v4_0_partner(self) -> None:
        torch_boundary = v4_fixed_radius.fixed_radius_count_threshold_2d_device_array_claim_boundary_v4("torch")
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual("measured_on_v4_section8_pod", torch_boundary["partner_claim_status"])
        self.assertEqual((), torch_boundary["partner_support_declared_unmeasured"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["second_primitive_work_authorized"])

        with self.assertRaisesRegex(ValueError, "partner must be one of"):
            v4_fixed_radius.fixed_radius_count_threshold_2d_device_array_claim_boundary_v4("cupy")

        with self.assertRaisesRegex(ValueError, "partner must be one of"):
            v4_fixed_radius.fixed_radius_count_threshold_2d_device_array_claim_boundary_v4("numpy")

    def test_prepared_session_wraps_native_device_column_route_with_v4_metadata(self) -> None:
        calls: dict[str, object] = {}
        fake_prepared = FakePrepared()

        def fake_prepare(search_point_columns, *, max_radius, partner):
            calls["prepare"] = {
                "search_point_columns": search_point_columns,
                "max_radius": max_radius,
                "partner": partner,
            }
            return fake_prepared

        def fake_allocate(query_count, *, partner):
            calls["allocate"] = {"query_count": query_count, "partner": partner}
            return {"query_ids": "ids_out", "neighbor_counts": "counts_out", "threshold_flags": "flags_out"}

        def fake_run(prepared, query_point_columns, *, radius, threshold, partner, output_columns, return_metadata):
            calls["run"] = {
                "prepared": prepared,
                "query_point_columns": query_point_columns,
                "radius": radius,
                "threshold": threshold,
                "partner": partner,
                "output_columns": output_columns,
                "return_metadata": return_metadata,
            }
            return {
                "columns": output_columns,
                "metadata": {
                    "adapter": "lower_level_adapter",
                    "whole_app_speedup_claim_authorized": True,
                },
            }

        original_prepare = v4_fixed_radius.prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene
        original_allocate = v4_fixed_radius.allocate_fixed_radius_count_threshold_2d_partner_device_output_columns
        original_run = v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns
        try:
            v4_fixed_radius.prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene = fake_prepare
            v4_fixed_radius.allocate_fixed_radius_count_threshold_2d_partner_device_output_columns = fake_allocate
            v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns = fake_run

            with v4_fixed_radius.prepare_fixed_radius_count_threshold_2d_device_arrays_v4(
                {"ids": "search_ids"},
                max_radius=0.35,
                partner="torch",
            ) as session:
                outputs = session.allocate_outputs(4)
                result = session.run(
                    {"ids": "query_ids"},
                    radius=0.25,
                    threshold=3,
                    output_columns=outputs,
                    return_metadata=True,
                )
        finally:
            v4_fixed_radius.prepare_fixed_radius_count_threshold_2d_optix_partner_device_scene = original_prepare
            v4_fixed_radius.allocate_fixed_radius_count_threshold_2d_partner_device_output_columns = original_allocate
            v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns = original_run

        self.assertTrue(fake_prepared.entered)
        self.assertTrue(fake_prepared.closed)
        self.assertEqual("torch", calls["prepare"]["partner"])
        self.assertEqual(4, calls["allocate"]["query_count"])
        self.assertIs(calls["run"]["prepared"], fake_prepared)
        self.assertEqual(3, calls["run"]["threshold"])
        self.assertEqual(outputs, result["columns"])
        metadata = result["metadata"]
        self.assertEqual("v4_fixed_radius_count_threshold_2d_device_arrays", metadata["adapter"])
        self.assertEqual("FIXED_RADIUS_COUNT_THRESHOLD_2D", metadata["generic_primitive"])
        self.assertTrue(metadata["measured_partner"])
        self.assertFalse(metadata["release_claim_authorized"])
        self.assertFalse(metadata["whole_app_speedup_claim_authorized"])
        self.assertFalse(metadata["second_primitive_work_authorized"])

    def test_run_can_return_columns_only(self) -> None:
        fake_prepared = FakePrepared()

        def fake_run(*args, **kwargs):
            return {"columns": {"threshold_flags": "flags"}, "metadata": {}}

        original_run = v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns
        try:
            v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns = fake_run
            session = v4_fixed_radius.V4FixedRadiusCountThreshold2DDeviceArraySession(
                prepared=fake_prepared,
                partner="torch",
                max_radius=1.0,
            )
            columns = session.run({}, radius=0.1, output_columns={}, return_metadata=False)
        finally:
            v4_fixed_radius.fixed_radius_count_threshold_2d_optix_prepared_partner_device_columns = original_run

        self.assertEqual({"threshold_flags": "flags"}, columns)


if __name__ == "__main__":
    unittest.main()
