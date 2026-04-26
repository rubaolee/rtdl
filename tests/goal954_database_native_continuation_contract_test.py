import sys
import unittest
from unittest import mock

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples import rtdl_database_analytics_app as db_app
from examples import rtdl_sales_risk_screening as sales
from examples import rtdl_v0_7_db_app_demo as regional


class _FakeInner:
    transfer = "columnar"


class _FakeDbDataset:
    def __init__(self, *, row_count: int = 14) -> None:
        self._dataset = _FakeInner()
        self.row_count = row_count

    def conjunctive_scan_count(self, predicates) -> int:
        return 6

    def conjunctive_scan(self, predicates):
        return ({"row_id": 1},)

    def grouped_count(self, query):
        return ({"region": "east", "count": 4},)

    def grouped_sum(self, query):
        return ({"region": "east", "sum": 900},)

    def grouped_count_summary(self, query):
        return {"east": 4, "west": 2}

    def grouped_sum_summary(self, query):
        return {"east": 900, "west": 240}

    def close(self) -> None:
        pass


class _MaterializingDbDataset:
    def __init__(self) -> None:
        self._dataset = _FakeInner()
        self.row_count = 14

    def conjunctive_scan_count(self, predicates) -> int:
        return 6

    def conjunctive_scan(self, predicates):
        return ({"row_id": 1},)

    def grouped_count(self, query):
        return ({"region": "east", "count": 4},)

    def grouped_sum(self, query):
        return ({"region": "east", "sum": 900},)

    def close(self) -> None:
        pass


class Goal954DatabaseNativeContinuationContractTest(unittest.TestCase):
    def test_regional_compact_summary_reports_native_continuation_only_when_materialization_free(self) -> None:
        with mock.patch.object(regional, "_prepare_dataset", return_value=_FakeDbDataset()):
            with regional.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")
        self.assertFalse(any("materialize" in phase for phase in payload["run_phases"]))

    def test_sales_compact_summary_reports_native_continuation_only_when_materialization_free(self) -> None:
        with mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset(row_count=12)):
            with sales.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")
        self.assertFalse(any("materialize" in phase for phase in payload["run_phases"]))

    def test_unified_db_app_propagates_materialization_free_native_continuation(self) -> None:
        with (
            mock.patch.object(regional, "_prepare_dataset", return_value=_FakeDbDataset()),
            mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset(row_count=12)),
        ):
            payload = db_app.run_app("optix", output_mode="compact_summary", require_rt_core=True)

        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_db_compact_summary")
        self.assertTrue(payload["rt_core_accelerated"])
        for section in payload["sections"].values():
            self.assertTrue(section["native_continuation_active"])

    def test_unified_db_full_output_does_not_overstate_native_continuation(self) -> None:
        payload = db_app.run_app("cpu_python_reference", output_mode="full")

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertFalse(payload["rt_core_accelerated"])

    def test_materializing_compact_path_is_not_marked_native_continuation(self) -> None:
        with mock.patch.object(regional, "_prepare_dataset", return_value=_MaterializingDbDataset()):
            with regional.prepare_session("optix", copies=2) as session:
                payload = session.run(output_mode="compact_summary")

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertTrue(any("materialize" in phase for phase in payload["run_phases"]))

    def test_unified_materializing_compact_path_is_not_rt_core_accelerated(self) -> None:
        with (
            mock.patch.object(regional, "_prepare_dataset", return_value=_MaterializingDbDataset()),
            mock.patch.object(sales, "_prepare_dataset", return_value=_FakeDbDataset(row_count=12)),
        ):
            payload = db_app.run_app("optix", output_mode="compact_summary", require_rt_core=True)

        self.assertFalse(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "none")
        self.assertFalse(payload["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
