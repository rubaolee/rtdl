from __future__ import annotations

import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_point_group as pg_v4


class V4PointGroupDeviceArrayApiTest(unittest.TestCase):
    def test_claim_boundary_is_measured_and_not_release_surface(self) -> None:
        torch_boundary = pg_v4.point_group_nearest_witness_2d_device_array_claim_boundary_v4("torch")
        cupy_boundary = pg_v4.point_group_nearest_witness_2d_device_array_claim_boundary_v4("cupy")

        self.assertEqual(
            "v4_point_group_nearest_witness_2d_device_arrays",
            torch_boundary["v4_api_surface"],
        )
        self.assertTrue(torch_boundary["measured_partner"])
        self.assertEqual(("torch",), torch_boundary["measured_partners"])
        self.assertEqual(("cupy",), torch_boundary["partner_support_declared_unmeasured"])
        self.assertEqual(
            "measured_on_v4_goal4618_pod_optix8",
            torch_boundary["partner_claim_status"],
        )
        self.assertEqual("8.0", torch_boundary["validated_optix_abi"])
        self.assertEqual("float32_computed_float64_output", torch_boundary["distance_precision"])
        self.assertFalse(torch_boundary["optix_9_1_validated"])
        self.assertEqual("declared_unmeasured_not_performance_ready", cupy_boundary["partner_claim_status"])
        self.assertTrue(torch_boundary["native_prepared_search_groups_owned_by_rtdl"])
        self.assertTrue(torch_boundary["query_point_columns_partner_owned"])
        self.assertTrue(torch_boundary["output_columns_partner_owned"])
        self.assertFalse(torch_boundary["host_query_upload_in_hot_path"])
        self.assertFalse(torch_boundary["host_materialization_in_hot_path"])
        self.assertFalse(torch_boundary["true_zero_copy_authorized"])
        self.assertFalse(torch_boundary["release_claim_authorized"])
        self.assertFalse(torch_boundary["broad_v4_speedup_claim_authorized"])

    def test_session_run_uses_device_query_and_device_output_route(self) -> None:
        prepared = _FakePreparedPointGroup()
        output_columns = {
            "query_ids": object(),
            "neighbor_ids": object(),
            "distances": object(),
        }
        query_columns = {"ids": object(), "x": object(), "y": object()}
        session = pg_v4.V4PointGroupNearestWitness2DDeviceArraySession(
            prepared=prepared,
            partner="torch",
            max_radius=2.0,
        )

        result = session.run(
            query_columns,
            radius=1.0,
            output_columns=output_columns,
            return_metadata=True,
        )

        self.assertIs(result["columns"], output_columns)
        metadata = result["metadata"]
        self.assertEqual("v4_point_group_nearest_witness_2d_device_arrays", metadata["adapter"])
        self.assertEqual("POINT_GROUP_NEAREST_WITNESS_2D", metadata["generic_primitive"])
        self.assertEqual(
            "write_device_nearest_witness_columns_from_device_query_columns",
            metadata["native_prepared_route"],
        )
        self.assertTrue(metadata["native_direct_device_output_columns"])
        self.assertFalse(metadata["host_query_upload_in_hot_path"])
        self.assertFalse(metadata["neighbor_rows_downloaded_to_host_in_hot_path"])
        self.assertFalse(metadata["host_materialization_in_hot_path"])
        self.assertEqual(1, prepared.device_query_calls)


class _FakePreparedPointGroup:
    def __init__(self) -> None:
        self.device_query_calls = 0

    def write_device_nearest_witness_columns_from_device_query_columns(
        self,
        query_point_columns,
        *,
        radius,
        query_ids_out,
        neighbor_ids_out,
        distances_out,
    ):
        self.device_query_calls += 1
        return {
            "metadata": {
                "backend": "optix",
                "native_symbol": "rtdl_optix_write_prepared_point_group_nearest_witness_2d_device_query_columns",
                "materializes_neighbor_rows": False,
                "direct_device_handoff_authorized": True,
                "query_point_columns_direct_device_read_confirmed": True,
                "output_columns_direct_device_write_confirmed": True,
                "true_zero_copy_authorized": False,
                "rt_core_speedup_claim_authorized": False,
            }
        }


if __name__ == "__main__":
    unittest.main()
