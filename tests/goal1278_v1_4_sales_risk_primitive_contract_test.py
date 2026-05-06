from __future__ import annotations

import unittest
from unittest import mock

from examples import rtdl_sales_risk_screening as sales
import rtdsl as rt


class _FakeInner:
    transfer = "columnar"


class _FakeDbDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 12

    def compact_summary_batch(self, requests):
        return {
            "risky_scan_count": 4,
            "risky_order_count_by_region": {"east": 1, "west": 2, "central": 1},
            "risky_revenue_by_region": {"east": 310, "west": 430, "central": 260},
        }

    def last_compact_summary_batch_phase_timings(self):
        return {"risky_scan_count": {"traversal": 0.1}}

    def close(self) -> None:
        pass


class Goal1278V14SalesRiskPrimitiveContractTest(unittest.TestCase):
    def test_contract_helper_defines_sales_risk_compact_summary_scope(self) -> None:
        contract = rt.sales_risk_primitive_contract(
            backend="optix",
            output_mode="compact_summary",
            materialization_free=True,
        )

        self.assertEqual(contract["app_row"], "database_analytics.sales_risk")
        self.assertEqual(contract["primitive"], "COUNT_HITS")
        self.assertEqual(contract["alternate_primitive"], "REDUCE_INT(COUNT)")
        self.assertEqual(contract["secondary_primitive"], "REDUCE_INT(SUM)")
        self.assertEqual(contract["backend_scope"], ("embree", "optix"))
        self.assertEqual(contract["backend_contract_role"], "nvidia_rt_target")
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertTrue(contract["materialization_free"])
        self.assertIn("SQL engines", contract["claim_boundary"])
        self.assertEqual(contract["migration_status"], "compatibility_wrapper_metadata_only")

    def test_optix_compact_summary_attaches_materialization_free_contract(self) -> None:
        with mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset()):
            with sales.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")
        self.assertEqual(contract["backend"], "optix")
        self.assertEqual(contract["backend_contract_role"], "nvidia_rt_target")
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertTrue(contract["materialization_free"])
        self.assertEqual(contract["mode"], "prepared_compact_summary")
        self.assertEqual(contract["prepared_state"], "prepared_columnar_dataset_reusable")
        self.assertIn("query_compact_summary_batch_sec", payload["run_phases"])

    def test_embree_compact_summary_attaches_cpu_rt_baseline_contract(self) -> None:
        with mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset()):
            with sales.prepare_session("embree", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        contract = payload["primitive_contract"]
        self.assertEqual(payload["native_continuation_backend"], "embree_db_compact_summary")
        self.assertEqual(contract["backend"], "embree")
        self.assertEqual(contract["backend_contract_role"], "cpu_rt_baseline_and_fallback")
        self.assertTrue(contract["active_v1_4_backend"])
        self.assertTrue(contract["same_contract_baseline_required"])
        self.assertTrue(contract["materialization_free"])

    def test_vulkan_existing_path_is_marked_inactive_for_v1_4(self) -> None:
        with mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset()):
            with sales.prepare_session("vulkan", copies=2) as session:
                with self.assertRaisesRegex(ValueError, "frozen before v2.1"):
                    session.run(output_mode="compact_summary")

    def test_materializing_output_is_not_marked_as_compact_primitive(self) -> None:
        payload = sales.run_case("cpu_python_reference", copies=1, output_mode="summary")
        contract = payload["primitive_contract"]

        self.assertEqual(contract["primitive"], "row_materialization")
        self.assertFalse(contract["materialization_free"])
        self.assertEqual(contract["prepared_state"], "none_required_for_materializing_rows")


if __name__ == "__main__":
    unittest.main()
