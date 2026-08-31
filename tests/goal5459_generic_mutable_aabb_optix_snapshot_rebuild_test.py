from __future__ import annotations

import os
import unittest
from pathlib import Path

import rtdsl as rt


OPTIX_LIBRARY = os.environ.get("RTDL_OPTIX_LIB")


@unittest.skipUnless(
    OPTIX_LIBRARY and Path(OPTIX_LIBRARY).is_file(),
    "RTDL_OPTIX_LIB is required for mutable AABB OptiX runtime parity",
)
class Goal5459GenericMutableAabbOptixSnapshotRebuildTest(unittest.TestCase):
    _FAULT_ENV = "RTDL_OPTIX_TEST_AABB_REFIT_FAULT"

    def test_immutable_optix_prepare_does_not_pay_for_or_allow_refit(self):
        prepared = rt.prepare_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(9,), backend="optix"
        )
        try:
            with self.assertRaisesRegex(RuntimeError, "does not allow sparse refit"):
                prepared.refit_updates(((9, (2.0, 2.0, 3.0, 3.0)),))
        finally:
            prepared.close()

    def test_optix_snapshot_rebuild_lifecycle_matches_expected_rows(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 1.5, 1.5)),
            indexed_ids=(10, 20),
            backend="optix",
        )
        query = ((0.25, 0.25, 0.75, 0.75),)
        self.assertEqual(
            index.intersection_rows(query, query_ids=(900,), row_capacity=8),
            ((900, 10), (900, 20)),
        )

        update_result = index.update(((20, (5.0, 5.0, 6.0, 6.0)),))
        self.assertEqual(
            update_result["mutation_execution_model"],
            "native_sparse_slot_refit_with_rollback",
        )
        self.assertEqual(
            index.intersection_rows(query, query_ids=(900,), row_capacity=8),
            ((900, 10),),
        )

        delete_result = index.delete((10,))
        self.assertEqual(delete_result["mutation_execution_model"], "atomic_snapshot_rebuild")
        self.assertEqual(index.intersection_rows(query, query_ids=(900,), row_capacity=8), ())

        inserted = index.insert(((0.4, 0.4, 0.6, 0.6),), ids=(30,))
        self.assertEqual(inserted["inserted_ids"], [30])
        self.assertEqual(inserted["mutation_execution_model"], "atomic_snapshot_rebuild")
        self.assertEqual(
            index.intersection_rows(query, query_ids=(900,), row_capacity=8),
            ((900, 30),),
        )
        self.assertEqual(
            index.metadata()["execution_model"],
            "native_fixed_cardinality_refit_or_atomic_snapshot_rebuild",
        )
        self.assertTrue(index.metadata()["native_incremental_update"])
        self.assertFalse(index.metadata()["native_incremental_insert_delete"])
        self.assertEqual(index.revision, 3)

        index.clear()
        self.assertEqual(index.active_count, 0)
        self.assertEqual(index.count(operation="range_intersects")["counts"], {"range_intersects": 0})
        index.close()

    def test_optix_point_rows_keep_stable_ids_after_update(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(77,), backend="optix"
        )
        self.assertEqual(
            index.point_membership_rows(((0.5, 0.5),), query_ids=(5,), row_capacity=4),
            ((5, 77),),
        )
        update_result = index.update(((77, (2.0, 2.0, 3.0, 3.0)),))
        self.assertEqual(
            update_result["mutation_execution_model"],
            "native_sparse_slot_refit_with_rollback",
        )
        self.assertEqual(
            index.point_membership_rows(((0.5, 0.5),), query_ids=(5,), row_capacity=4),
            (),
        )
        index.close()

    def test_sparse_refit_post_write_failure_restores_records_and_gas(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(77,), backend="optix"
        )
        try:
            os.environ[self._FAULT_ENV] = "primary_after_device_and_gas_update"
            with self.assertRaisesRegex(
                RuntimeError, "primary_after_device_and_gas_update"
            ):
                index.update(((77, (2.0, 2.0, 3.0, 3.0)),))
            os.environ.pop(self._FAULT_ENV, None)

            self.assertEqual(index.revision, 0)
            self.assertEqual(
                index.point_membership_rows(
                    ((0.5, 0.5),), query_ids=(5,), row_capacity=4
                ),
                ((5, 77),),
            )
            self.assertEqual(
                index.point_membership_rows(
                    ((2.5, 2.5),), query_ids=(6,), row_capacity=4
                ),
                (),
            )

            result = index.update(((77, (2.0, 2.0, 3.0, 3.0)),))
            self.assertEqual(
                result["mutation_execution_model"],
                "native_sparse_slot_refit_with_rollback",
            )
            self.assertEqual(index.revision, 1)
        finally:
            os.environ.pop(self._FAULT_ENV, None)
            index.close()

    def test_sparse_refit_rollback_failure_poison_handle_fail_closed(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(77,), backend="optix"
        )
        try:
            os.environ[self._FAULT_ENV] = "primary_and_rollback_after_restore_write"
            with self.assertRaisesRegex(RuntimeError, "rollback could not restore"):
                index.update(((77, (2.0, 2.0, 3.0, 3.0)),))
            os.environ.pop(self._FAULT_ENV, None)

            self.assertEqual(index.revision, 0)
            with self.assertRaisesRegex(RuntimeError, "invalid after failed rollback"):
                index.point_membership_rows(
                    ((0.5, 0.5),), query_ids=(5,), row_capacity=4
                )
            with self.assertRaisesRegex(RuntimeError, "invalid after failed rollback"):
                index.intersection_rows(
                    ((0.0, 0.0, 1.0, 1.0),), query_ids=(6,), row_capacity=4
                )
            with self.assertRaisesRegex(RuntimeError, "invalid after failed rollback"):
                index.count(point_queries=((0.5, 0.5),), operation="point_contains")
            with self.assertRaisesRegex(RuntimeError, "invalid after failed rollback"):
                index.update(((77, (4.0, 4.0, 5.0, 5.0)),))
        finally:
            os.environ.pop(self._FAULT_ENV, None)
            index.close()


if __name__ == "__main__":
    unittest.main()
