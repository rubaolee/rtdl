from __future__ import annotations

import inspect
import unittest
from unittest import mock

import rtdsl as rt
import rtdsl.mutable_aabb_index as mutable_aabb


def dynamic_obstacle_contact_pairs(index: rt.MutableAabbIndex2D):
    return index.intersection_rows(((0.25, 0.25, 0.75, 0.75),), query_ids=(900,))


class Goal5458GenericMutableAabbIndexContractTest(unittest.TestCase):
    def test_cpu_lifecycle_preserves_stable_ids(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 1.5, 1.5)),
            indexed_ids=(10, 20),
        )
        self.assertEqual(dynamic_obstacle_contact_pairs(index), ((900, 10), (900, 20)))

        updated = index.update(((20, (5.0, 5.0, 6.0, 6.0)),))
        self.assertEqual(updated["revision_after"], 1)
        self.assertEqual(dynamic_obstacle_contact_pairs(index), ((900, 10),))

        deleted = index.delete((10,))
        self.assertEqual(deleted["deleted_ids"], [10])
        self.assertEqual(dynamic_obstacle_contact_pairs(index), ())

        inserted = index.insert(((0.4, 0.4, 0.6, 0.6),), ids=(30,))
        self.assertEqual(inserted["inserted_ids"], [30])
        self.assertEqual(dynamic_obstacle_contact_pairs(index), ((900, 30),))

        cleared = index.clear()
        self.assertTrue(cleared["cleared"])
        self.assertEqual(index.active_ids, ())
        self.assertEqual(dynamic_obstacle_contact_pairs(index), ())
        self.assertEqual(index.count(operation="range_intersects")["counts"], {"range_intersects": 0})

    def test_failed_batch_keeps_previous_revision_and_rows(self):
        index = rt.prepare_mutable_aabb_index_2d(
            ((0.0, 0.0, 1.0, 1.0),), indexed_ids=(7,)
        )
        before = dynamic_obstacle_contact_pairs(index)
        with self.assertRaises(KeyError):
            index.apply_mutations(updates=((99, (2.0, 2.0, 3.0, 3.0)),))
        self.assertEqual(index.revision, 0)
        self.assertEqual(dynamic_obstacle_contact_pairs(index), before)
        with self.assertRaises(ValueError):
            index.apply_mutations(
                insert_boxes=((2.0, 2.0, 3.0, 3.0),), insert_ids=(7,)
            )
        self.assertEqual(index.active_ids, (7,))

        with mock.patch.object(
            mutable_aabb,
            "prepare_aabb_index_2d",
            side_effect=RuntimeError("synthetic rebuild failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic rebuild failure"):
                index.update(((7, (3.0, 3.0, 4.0, 4.0)),))
        self.assertEqual(index.revision, 0)
        self.assertEqual(index.active_ids, (7,))
        self.assertEqual(dynamic_obstacle_contact_pairs(index), before)

    def test_auto_ids_are_monotonic_until_clear(self):
        index = rt.prepare_mutable_aabb_index_2d()
        first = index.insert(((0.0, 0.0, 1.0, 1.0),))
        self.assertEqual(first["inserted_ids"], [0])
        index.delete((0,))
        second = index.insert(((2.0, 2.0, 3.0, 3.0),))
        self.assertEqual(second["inserted_ids"], [1])
        reset = index.apply_mutations(
            clear=True, insert_boxes=((4.0, 4.0, 5.0, 5.0),)
        )
        self.assertEqual(reset["inserted_ids"], [0])

    def test_contract_is_explicitly_snapshot_rebuild_not_native_refit(self):
        contract = rt.MUTABLE_AABB_INDEX_2D_CONTRACT
        self.assertEqual(
            contract["execution_model"],
            "native_fixed_cardinality_refit_or_atomic_snapshot_rebuild",
        )
        self.assertTrue(contract["native_incremental_update"])
        self.assertFalse(contract["native_incremental_insert_delete"])
        self.assertEqual(contract["app_semantics"], "none")
        source = inspect.getsource(mutable_aabb).lower()
        for forbidden in ("librts", "rtspatial", "paper", "ray multicast"):
            self.assertNotIn(forbidden, source)
        consumer = inspect.getsource(dynamic_obstacle_contact_pairs).lower()
        self.assertNotIn("librts", consumer)
        self.assertIn("obstacle", consumer)

    def test_closed_and_invalid_batches_fail_closed(self):
        index = rt.prepare_mutable_aabb_index_2d(((0.0, 0.0, 1.0, 1.0),))
        with self.assertRaises(ValueError):
            index.apply_mutations(clear=True, delete_ids=(0,))
        index.close()
        with self.assertRaisesRegex(RuntimeError, "closed"):
            index.count(operation="point_contains")

    def test_query_id_lengths_fail_closed(self):
        index = rt.prepare_mutable_aabb_index_2d(((0.0, 0.0, 1.0, 1.0),))
        with self.assertRaisesRegex(ValueError, "point_queries length"):
            index.point_membership_rows(((0.5, 0.5),), query_ids=())
        with self.assertRaisesRegex(ValueError, "query_boxes length"):
            index.intersection_rows(((0.0, 0.0, 1.0, 1.0),), query_ids=())


if __name__ == "__main__":
    unittest.main()
